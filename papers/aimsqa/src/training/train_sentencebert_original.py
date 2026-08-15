import pandas as pd
import ast
from sentence_transformers import SentenceTransformer, InputExample, losses, util
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split

import torch

input_query = {
        "approval":"Was the company's Modern Slavery Act statement approved by the Board of Directors (or equivalent management body)?",
        "signature":"Was the company’s Modern Slavery Act statement signed by an appropriate person?",
        "c1 (reporting entity)":"",
        "c2 (structure)":"Does the company disclose its ownership structure?",
        "c2 (operations)":"Does the company disclose the operations?",
        "c2 (supply chains)":"Does the company identify suppliers in its supply chain or the regions where its supply chain is?",
        "c3 (risk description)":"Did the company identify any specific risks or incidents related to modern slavery?",
        "c4 (risk mitigation)":"Does the company outline specific actions or policies to address modern slavery in its supply chain?",
        "c4 (remediation)":"Did the company explain the corrective steps it has taken (or would take) in response to modern slavery incidents in their own operations and/or supply chain?",
        "c5 (effectiveness)":"Does the company define performance indicators that measure the effectiveness of their actions to combat slavery and trafficking?",
        "c6 (consultation)":"Does the statement mention consulting with any entities the company owns or controls?"
}
labels = list(input_query.keys())

def create_context(df, window=5):
    # Ensure correct ordering
    df = df.sort_values(by=['statement_id', 'sentence_id']).reset_index(drop=True)

    def add_context(group):
        sentences = group['sentence'].tolist()
        context_list = []
        for i in range(len(sentences)):
            start = max(0, i - window)
            end = i + window + 1
            context = ' '.join(sentences[start:i] + [sentences[i]] + sentences[i+1:end])
            context_list.append(context)
        group['context'] = context_list
        return group

    return df.groupby('statement_id', group_keys=False).apply(add_context)

data = pd.read_csv("AU_train.csv")
data.sentence.fillna(" ", inplace=True)
df0 = create_context(data)

targets = df0.targets.tolist()
targets = [ast.literal_eval(t) for t in targets]

sentences = df0.sentence.tolist()
context = df0.context.tolist()
statement_id = df0.statement_id.tolist()
sentence_id = df0.sentence_id.tolist()

final_sid = []
final_senid = []
criteria = []
answer = []
final_sentence = []
final_context = []
for idx, t in enumerate(targets):
    for i,l in zip(t, labels):
        if i == -1:
            continue
        if i == 0:
            this_answer = "No"
        else:
            this_answer = "Yes"
        final_sid.append(statement_id[idx])
        final_senid.append(sentence_id[idx])
        criteria.append(l)
        answer.append(this_answer)
        final_sentence.append(sentences[idx])
        final_context.append(context[idx])

new_df = pd.DataFrame({"statement_id":final_sid,
             "sentence_id":final_senid,
             "criteria":criteria,
             "answer":answer,
             "sentence_text": final_sentence,
             "text_with_context":final_context})

sampled_list = []

# Group by each unique criteria
for crit in new_df['criteria'].unique():
    group = new_df[new_df['criteria'] == crit]
    
    # Sample 1000 'Yes' and 1000 'No' if possible
    yes_sample = group[group['answer'] == "Yes"].sample(n=min(10000, len(group[group['answer'] == "Yes"])), random_state=42)
    no_sample = group[group['answer'] == "No"].sample(n=min(10000, len(group[group['answer'] == "No"])), random_state=42)
    
    # Combine and append
    sampled = pd.concat([yes_sample, no_sample])
    sampled_list.append(sampled)

# Concatenate all samples
df = pd.concat(sampled_list).reset_index(drop=True)

# ==== Check device ====
device = "cuda" if torch.cuda.is_available() else "CPU"
#device = "mps"
print(f"Using device: {device}")

# ==== Load or Simulate Data ====

df["label"] = df["answer"].apply(lambda x: 1.0 if x.lower() == "yes" else 0.0)
df["query"] = df["criteria"].apply(lambda x: input_query[x])
print(df)
# ==== Split Data ====
train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

train_examples = [
    InputExample(texts=[row.query, row.text_with_context], label=row.label)
    for _, row in train_df.iterrows()
]
val_examples = [
    InputExample(texts=[row.query, row.text_with_context], label=row.label)
    for _, row in val_df.iterrows()
]

# ==== Load Model to GPU ====
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=32)
train_loss = losses.CosineSimilarityLoss(model)

# ==== Training Loop with Validation ====
epochs = 5
threshold = 0.7  # cosine similarity threshold to classify as "Yes"

for epoch in range(epochs):
    print(f"\nEpoch {epoch+1}/{epochs}")

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=1,
        warmup_steps=10,
        show_progress_bar=True
    )

    # === Validation ===
    print("Running validation...")
    correct = 0
    total = 0

    for ex in val_examples:
        query, passage = ex.texts
        query_emb = model.encode(query, convert_to_tensor=True, device=device)
        passage_emb = model.encode(passage, convert_to_tensor=True, device=device)

        score = util.cos_sim(query_emb, passage_emb).item()
        prediction = 1.0 if score >= threshold else 0.0
        is_correct = prediction == ex.label
        correct += int(is_correct)
        total += 1
        # print(f"Query: {query} | Score: {score:.2f} | Label: {ex.label} | Pred: {prediction} | Correct: {is_correct}")

    accuracy = correct / total
    print(f"Validation Accuracy after epoch {epoch+1}: {accuracy:.2%}")

# ==== Save the trained model ====
model.save("./output_retriever_win5")

