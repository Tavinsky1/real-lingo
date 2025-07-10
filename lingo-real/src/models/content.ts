export interface Content {
    id: number;
    type: 'tongueTwister' | 'famousQuote' | 'regionalExpression' | 'joke' | 'insult';
    text: string;
    language: string;
    createdAt: Date;
}