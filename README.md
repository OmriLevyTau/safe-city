# Table of Contents
- [Mr Know All](#mr-know-all)
- [How does it work?](#how-does-it-work)
- [Running the project](#running-the-project)


# Mr Know All.

Mr. Know All offers enables you to upload and store your data.
Once uploaded, you can immediately access an AI assistant that can answer your questions based on your own data.
You can enjoy the benefits of a chatGPT-level AI assistant, even with your most recent data, without having to train your own model or fine-tune an existing one.

## How does it work?


First, you upload your data.
We break your documents into sentences, embed each one into a vector using a dedicated pipeline. 
Finally, we store them in a vector database that is best suited for semantic search.

![upload-workflow](https://github.com/OmriLevyTau/webui/blob/main/src/images/workflow-upload.png)

Now you can ask your question.
We retrieve the most relevant data from the vector database and inject it into ChatGPT along with your question. 
we prompt the system to generate the best answer based on your data.

![ask-workflow](https://github.com/OmriLevyTau/webui/blob/main/src/images/workflow-ask.png)