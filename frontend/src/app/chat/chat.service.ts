import { HttpClient, HttpDownloadProgressEvent, HttpEventType, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, filter, tap } from 'rxjs';

export interface ChatMessageFile {
    name: string;
    mime_type: string;
}

export interface ChatMessage {
    author: string;
    content?: string;
    files?: ChatMessageFile[];
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

export interface StreamedEvent {
    type: string;
    value: string;
}


@Injectable({
    providedIn: 'root'
})
export class ChatService {

    public chats: ChatSessionHeader[] = [];
    public chat!: ChatSession;
    public isLoading = false;
    public isDeleting = false;
    public waitingForResponse = false;
    public isTyping = false;

    private readonly endpoint = '/api/chats';
    private pingIntervalId: any;

    constructor(private readonly httpClient: HttpClient) { }

    connect() {
        // Set a timeout to keep the connection alive
        this.pingIntervalId = setInterval(() => this.httpClient.get<void>("/api/ping").subscribe(), 60000);
    }

    disconect() {
        clearInterval(this.pingIntervalId);
    }

    get_models(): Observable<string[]> {
        return this.httpClient.get<string[]>(`/api/models`);
    }

    new(): Observable<ChatSession> {
        return this.get("_NEW_");
    }

    get(chat_session_id: string): Observable<ChatSession> {
        this.isLoading = true;
        return this.httpClient.get<ChatSession>(`${this.endpoint}/${chat_session_id}`)
            .pipe(tap(chat => {
                this.chat = chat;
                this.isLoading = false;
            }));
    }

    send_async(agent: string, message: ChatMessage): Observable<StreamedEvent> {
        if (this.chat && !this.chats.some(chat => chat.chat_session_id == this.chat.chat_session_id)) {
            this.chats.unshift({
                chat_session_id: this.chat.chat_session_id,
                user: "",
                created: new Date(),
                summary: message.content
            });
        }
        let lastCommaIndex = 0;
        return new Observable(observer => {
            let buffer = '';
            let params = new HttpParams().set('agent', agent);
            this.httpClient.post(`${this.endpoint}/${this.chat.chat_session_id}/messages`, message, {
                params: params,
                responseType: 'text',
                reportProgress: true,
                observe: 'events'
            })
                .pipe(filter(event => event.type === HttpEventType.DownloadProgress && (event as HttpDownloadProgressEvent).partialText != undefined))
                .subscribe({
                    next: (data) => {
                        let buffer = (data as HttpDownloadProgressEvent).partialText ?? '';
                        let i;
                        while ((i = buffer.indexOf('\n', lastCommaIndex + 1)) > -1) {
                            try {
                                let jsonStr = buffer.substring(lastCommaIndex, i);
                                if (jsonStr.startsWith(","))
                                    jsonStr = jsonStr.substring(1)
                                const item = JSON.parse(jsonStr) as StreamedEvent;
                                observer.next(item);
                                lastCommaIndex = i + 1;
                            } catch (e) {
                            }
                        }
                    },
                    error: (err) => observer.error(err),
                    complete: () => {
                        if (buffer) {
                            try {
                                const item = JSON.parse(buffer) as StreamedEvent;
                                observer.next(item);
                            } catch (e) {
                            }
                        }
                        observer.complete();
                    },
                });
        });
    }

    get_all(): Observable<ChatSessionHeader[]> {
        return this.httpClient.get<ChatSessionHeader[]>(this.endpoint)
            .pipe(tap(chats => this.chats = chats));
    }

    delete(chat_session_id: string): Observable<void> {
        this.isDeleting = true;
        return this.httpClient.delete<void>(`${this.endpoint}/${chat_session_id}`)
            .pipe(tap(() => {
                this.chats = this.chats.filter(chat => chat.chat_session_id !== chat_session_id);
                this.isDeleting = false;
            }));
    }

    putChatSession(chatSession: ChatSession): Observable<void> {
        return this.httpClient.put<void>(`${this.endpoint}/${chatSession.chat_session_id}`, chatSession);
    }

}
