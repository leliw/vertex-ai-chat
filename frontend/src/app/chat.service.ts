import { HttpClient, HttpDownloadProgressEvent, HttpEventType } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, filter, map } from 'rxjs';

export interface ChatMessage {
    author: string;
    content?: string;
}

export interface ChatSessionHeader {
    chat_session_id: string;
    user: string;
    created: Date;
    summary?: string;
}

export interface ChatSession extends ChatSessionHeader {
    history: ChatMessage[];
}

@Injectable({
    providedIn: 'root'
})
export class ChatService {

    private endpoint = '/api/chat';
    private connected$ = new BehaviorSubject<boolean>(false);

    constructor(private httpClient: HttpClient) { }

    connect() {
        // Unused
    }

    disconect() {
        // Unused
    }

    new(): Observable<ChatSession> {
        return this.httpClient.get<ChatSession>(`${this.endpoint}/_NEW_`);
    }

    get(chat_session_id: string): Observable<ChatSession> {
        return this.httpClient.get<ChatSession>(`${this.endpoint}/${chat_session_id}`);
    }

    send_async(message: ChatMessage): Observable<string> {
        let alreadyDownloaded = "";
        return this.httpClient.post(`${this.endpoint}/message`, message, {
            responseType: 'text',
            reportProgress: true,
            observe: 'events'
        }).pipe(
            filter(event => event.type === HttpEventType.DownloadProgress),
            map(event => {
                const partialText = (event as HttpDownloadProgressEvent).partialText
                if (partialText) {
                    const chunk = partialText.substring(alreadyDownloaded.length);
                    alreadyDownloaded = partialText;
                    return chunk;
                }
                return "";
            }));
    };

    connected(): Observable<boolean> {
        return this.connected$;
    }

    get_all(): Observable<ChatSessionHeader[]> {
        return this.httpClient.get<ChatSessionHeader[]>(this.endpoint);
    }

    delete(chat_session_id: string): Observable<void> {
        return this.httpClient.delete<void>(`${this.endpoint}/${chat_session_id}`);
    }
}
