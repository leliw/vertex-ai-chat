import { HttpClient, HttpDownloadProgressEvent, HttpEvent, HttpEventType, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, filter } from 'rxjs';

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

    private endpoint = '/api/chat';
    private connected$ = new BehaviorSubject<boolean>(false);
    private pingIntervalId: any;


    constructor(private httpClient: HttpClient) { }

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
        return this.httpClient.get<ChatSession>(`${this.endpoint}/_NEW_`);
    }

    get(chat_session_id: string): Observable<ChatSession> {
        return this.httpClient.get<ChatSession>(`${this.endpoint}/${chat_session_id}`);
    }

    send_async(model: string, message: ChatMessage): Observable<StreamedEvent> {
        let lastCommaIndex = 0;
        return new Observable(observer => {
            let buffer = '';
            let params = new HttpParams().set('model', model);
            this.httpClient.post(`${this.endpoint}/message`, message, {
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

    connected(): Observable<boolean> {
        return this.connected$;
    }

    get_all(): Observable<ChatSessionHeader[]> {
        return this.httpClient.get<ChatSessionHeader[]>(this.endpoint);
    }

    delete(chat_session_id: string): Observable<void> {
        return this.httpClient.delete<void>(`${this.endpoint}/${chat_session_id}`);
    }

    putChatSession(chatSession: ChatSession): Observable<void> {
        return this.httpClient.put<void>(`${this.endpoint}/${chatSession.chat_session_id}`, chatSession);
    }

    uploadFiles(formData: FormData): Observable<HttpEvent<void>> {
        return this.httpClient.post<void>(`/api/files`, formData, {
            reportProgress: true,
            observe: 'events'
        });
    }

    deleteFile(filename: string): Observable<void> {
        return this.httpClient.delete<void>(`/api/files/${filename}`);
    }
}
