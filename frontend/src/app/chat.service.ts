import { HttpClient, HttpDownloadProgressEvent, HttpEventType } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, filter, map } from 'rxjs';

export interface Message {
    author: string;
    content?: string;
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

    get(): Observable<Message[]> {
        return this.httpClient.get<Message[]>(this.endpoint);
    }

    send(message: Message): Observable<Message> {
        return this.httpClient.post<Message>(this.endpoint, message);
    }

    send_async(message: Message): Observable<string> {
        let alreadyDownloaded = "";
        return this.httpClient.post(this.endpoint + "/async", message, {
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

}
