import { Component, EventEmitter, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ChatService } from '../chat.service';

@Component({
    selector: 'app-chat-list',
    standalone: true,
    imports: [MatListModule, MatIconModule, MatButtonModule, MatTooltipModule],
    templateUrl: './chat-list.component.html',
    styleUrl: './chat-list.component.css'
})
export class ChatListComponent {
    @Output() loadEvent = new EventEmitter<string>();
    @Output() deleteEvent = new EventEmitter<string>();


    constructor(public chatService: ChatService) {
        this.chatService.get_all().subscribe();
    }

    loadChat(chat_session_id: string) {
        this.chatService.get(chat_session_id).subscribe();
        this.loadEvent.emit(chat_session_id);
    }

    deleteChat(chat_session_id: string) {
        this.chatService.delete(chat_session_id).subscribe(() => {
            this.deleteEvent.emit(chat_session_id);
        });
    }
}
