# Original SentenceBERT fine-tuning materials

`train_sentencebert_original.py` is an exact copy of `ft-sb/main.py`. It fine-tunes `all-MiniLM-L6-v2` with cosine-similarity loss using context windows of five sentences on either side and saves the result as `output_retriever_win5`.

The saved model used by the paper pipeline is already bundled at `../models/sentencebert_retriever`. The remaining generator scripts are retained as experiment provenance and are not required to run `../pipeline.py`.

The original training script uses CUDA-oriented environment assumptions and writes into its current directory. Run it only when reproducing training, preferably after changing its device fallback from the historical string `CPU` to PyTorch's lowercase `cpu` when CUDA is unavailable.
