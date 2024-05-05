import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

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

    connect() { }

    disconect() { }

    get(): Observable<Message[]> {
        return this.httpClient.get<Message[]>(this.endpoint);
    }
    
    send(message: Message): Observable<Message>{ 
        return this.httpClient.post<Message>(this.endpoint, message);
    }

    connected(): Observable<boolean> {
        return this.connected$;
    }

}
