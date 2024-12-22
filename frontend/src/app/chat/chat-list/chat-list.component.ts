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
    }
}
