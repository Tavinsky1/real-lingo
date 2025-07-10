export const formatText = (text: string): string => {
    return text.trim().replace(/\s+/g, ' ');
};

export const capitalizeFirstLetter = (text: string): string => {
    return text.charAt(0).toUpperCase() + text.slice(1);
};

export const formatQuote = (quote: string, author: string): string => {
    return `"${quote}" - ${author}`;
};

export const formatList = (items: string[]): string => {
    return items.join(', ');
};