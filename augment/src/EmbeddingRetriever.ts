import { logTitle } from "./utils";
import VectorStore from "./VectorStore";
import 'dotenv/config';

export default class EmbeddingRetriever {
    private embeddingModel: string;
    private vectorStore: VectorStore;

    constructor(embeddingModel: string) {
        this.embeddingModel = embeddingModel;
        this.vectorStore = new VectorStore();
    }

    async embedDocument(document: string) {
        logTitle('EMBEDDING DOCUMENT');
        const embedding = await this.embed(document);
        this.vectorStore.addEmbedding(embedding, document);
        return embedding;
    }

    async embedQuery(query: string) {
        logTitle('EMBEDDING QUERY');
        const embedding = await this.embed(query);
        return embedding;
    }

    private async embed(document: string): Promise<number[]> {
        const response = await fetch(`${process.env.EMBEDDING_BASE_URL}/embeddings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.EMBEDDING_KEY}`,
            },
            body: JSON.stringify({
                model: this.embeddingModel,
                input: document,
                encoding_format: 'float',
            }),
        });
        const data = await response.json();
        console.log(data.data[0].embedding);
        return data.data[0].embedding;
    }

    async retrieve(query: string, topK: number = 3): Promise<string[]> {
        const queryEmbedding = await this.embedQuery(query);
        return this.vectorStore.search(queryEmbedding, topK);
    }
}