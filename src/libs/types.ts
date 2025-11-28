export const colors: Record<string, string> = {
    happiness: "#fbc36fff",
    sadness: "#64B5F6",
    anger: "#E57373",
    fear: "#9575CD",
    disgust: "#81C784",
    surprise: "#4FC3F7",
    love: "#F06292",
    desire: "#F48FB1",
    guilt: "#A1887F",
    shame: "#8D6E63",
    sarcasm: "#BA68C8",
    confusion: "#90A4AE",
    neutral: "#BDBDBD"
};

export const platforms_icons: Record<string, string> = {
    "telegram": "telegram.svg",
    "discord": "discord.svg"
}

export interface Emotion {
    name: string;
    percent: number;
    x: number;
    y: number;
    r: number; 
    count: number | undefined;
}

export interface PlatformUser {
    id: number;
    platform: string;
    username: string;
    platform_user_id: string;
}

export interface EmotionStats {
    emotions: Array<Emotion>;
    total_messages: number;
    year: string | null;
}

export interface Profile {
    id: number;
    avatar: string | null;
    global_name: string;
    canonical_id: string;
    added_at: string;
    platform_users: Array<PlatformUser>;
    chats: Array<ChatType>;
}

export interface ChatType {
    id: number;
    name: string;
    avatar: string | null;
    type: string;
    participants: Array<Profile>;
}

export interface Media {
    type: string;
    path: string;
    thumbnail: string | null;
}

export interface MessageType {
    id: number;
    author_id: string;
    author_name: string;
    timestamp: string;
    avatar: string | null;
    text: string;
    emotion: string;
    chat_id: string;
    platform_id: number;
    reply: MessageType | null;
    media: Array<Media> | null;
    forwarded_from: string | null;
}
 
export interface EmotionStatsByYear {
    all_years: EmotionStats;
    by_year: Record<string, EmotionStats>;
}