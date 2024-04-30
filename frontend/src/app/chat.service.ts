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

    private connected$ = new BehaviorSubject<boolean>(false);
    
    constructor() { }

    connect() { }

    disconect() { }

    send(message: string) { }

    connected(): Observable<boolean> {
        return this.connected$;
    }

}
