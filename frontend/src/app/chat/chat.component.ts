import { Component, ElementRef, OnDestroy, OnInit, ViewChild, ViewEncapsulation, inject } from '@angular/core';
import { ChatService, ChatSessionHeader, ChatSession } from '../chat.service';
import { AsyncPipe, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSidenavContainer, MatSidenavModule } from '@angular/material/sidenav';
import { MatChipsModule } from '@angular/material/chips';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MarkdownPipe } from '../shared/markdown.pipe';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatToolbarModule } from '@angular/material/toolbar';
import { BehaviorSubject, Observable, Subscription, filter, first, firstValueFrom, map, shareReplay } from 'rxjs';
import { AuthService } from '../shared/auth/auth.service';
import { ConfigService } from '../shared/config/config.service';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { HttpEventType } from '@angular/common/http';


@Component({
    selector: 'app-chat',
    standalone: true,
    imports: [CommonModule,
        MatToolbarModule,
        MatChipsModule,
        MatButtonModule,
        MatSidenavModule,
        MatListModule,
        MatIconModule,
        AsyncPipe,
        FormsModule, MatInputModule, MatTooltipModule, MatMenuModule, MarkdownPipe, MatProgressSpinnerModule],
    templateUrl: './chat.component.html',
    styleUrl: './chat.component.css',
    encapsulation: ViewEncapsulation.None,
})
export class ChatComponent implements OnInit, OnDestroy {

    @ViewChild(MatSidenavContainer) drawerContainer!: MatSidenavContainer;
    @ViewChild('container') container!: ElementRef;

    models: string[] = [];
    model!: string;
    history: ChatSessionHeader[] = [];
    session!: ChatSession;
    sessionChanged = false;
    newMessage = '';
    isLoading = false;
    progressSpinner = false;
    waitingForResponse = false;
    connected = false;
    currentAnswer = '';
    currentTypeIndex = 0;
    actionButtons?: number = undefined;

    private dataSubscription!: Subscription;
    private breakpointObserver = inject(BreakpointObserver);

    isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
        .pipe(
            map(result => result.matches),
            shareReplay()
        );
    isHandset!: boolean;
    isUploading$: BehaviorSubject<boolean> = new BehaviorSubject(false);

    constructor(private chatService: ChatService, public authService: AuthService, private config: ConfigService) {
        // Get the initial messages from the server
        this.chatService.get_models().subscribe(models => {
            this.models = models;
            this.model = models[0];
            this.chatService.get_all().subscribe(history => {
                this.newChat()
                this.history = history;
                setTimeout(() => this.drawerContainer.updateContentMargins(), 100);
            });
        });
        this.isHandset$.subscribe(isHandset => this.isHandset = isHandset);
    }

    ngOnInit(): void {
        this.chatService.connect();
        this.chatService.connected().subscribe(connected => this.connected = connected);
    }

    ngOnDestroy(): void {
        this.chatService.disconect();
    }

    setModel(model: string) {
        this.model = model;
    }

    async sendMessageAsync() {
        // Send message to the server and process the response asynchronously
        if (this.newMessage.trim().length > 0) {
            if (this.session.history.length == 0 && !this.sessionChanged)
                this.history.unshift({
                    chat_session_id: this.session.chat_session_id,
                    user: "",
                    created: new Date(),
                    summary: this.newMessage
                });
            const files = this.selectedFiles.map(file => { return { name: file.name, mime_type: file.type } })
            const message = { author: "user", content: this.newMessage, files: files };

            if (this.sessionChanged) {
                await firstValueFrom(this.chatService.putChatSession(this.session));
                this.sessionChanged = false;
            }
            if (this.isUploading$.value)
                await firstValueFrom(this.isUploading$.pipe(filter(ul => !ul)));
            this.selectedFiles = [];
            this.uploadProgress = [];
            this.session.history.push(message);
            const newMessage = { author: "user", content: this.newMessage }
            this.scrollBottom();
            this.newMessage = '';
            this.waitingForResponse = true;
            this.currentAnswer = '';
            this.currentTypeIndex = 0;
            this.session.history.push({ author: "ai", content: "" });
            this.dataSubscription = this.chatService.send_async(this.model, newMessage).subscribe({
                next: (chunk) => {
                    if (chunk.type == "text") {
                        this.currentAnswer += chunk.value;
                        if (this.currentTypeIndex == 0)
                            this.typeAnswer();
                    } else if (chunk.type.startsWith("error")) {
                        this.stopTyping()
                        if (this.session.history[this.session.history.length - 1].author == "ai")
                            this.session.history.pop();
                        const errorClass = chunk.type.split(":")[1];
                        const errorMessage = "```\n" + chunk.value + "\n```"
                        this.session.history.push({ author: "error", content: `### ${errorClass}\n\n${errorMessage}` });
                        setTimeout(() => this.scrollBottom(), 100);
                    }
                },
                complete: () => {
                    this.waitingForResponse = false;
                }
            });
        }
    }

    typeAnswer() {
        // Simulate typing effect
        if (this.currentTypeIndex < this.currentAnswer.length) {
            this.session.history[this.session.history.length - 1].content += this.currentAnswer[this.currentTypeIndex];
            this.currentTypeIndex++;
            this.scrollBottom();
            setTimeout(() => this.typeAnswer(), 10);
        } else if (this.waitingForResponse)
            setTimeout(() => this.typeAnswer(), 10);
    }

    stopTyping() {
        // Stop typing
        this.currentTypeIndex = this.currentAnswer.length
        this.waitingForResponse = false;
    }

    scrollBottom(): void {
        // Scroll to the bottom of the chat container
        setTimeout(() => this.container.nativeElement.scrollTop = this.container.nativeElement.scrollHeight, 100);
    }

    newChat() {
        this.loadChat('_NEW_');
    }

    loadChat(chat_session_id: string) {
        this.isLoading = true;
        setTimeout(() => this.progressSpinner = this.isLoading, 500);
        this.chatService.get(chat_session_id).subscribe(session => {
            this.session = session;
            if (this.isHandset)
                this.drawerContainer.close();
            setTimeout(() => this.scrollBottom(), 100);
            this.isLoading = false;
            this.progressSpinner = false;
            this.newMessage = '';
            this.selectedFiles = [];
            this.uploadProgress = [];
            this.sessionChanged = false;
        });

    }

    cancelGenerating() {
        // Cancel the current request
        this.dataSubscription.unsubscribe();
        this.stopTyping();
        if (this.session.history[this.session.history.length - 1].author == "ai")
            this.session.history.pop();
        const question = this.session.history.pop();
        if (question)
            this.newMessage = question.content ?? '';
        this.chatService.putChatSession(this.session).subscribe();
    }

    deleteChat(chat_session_id: string) {
        this.chatService.delete(chat_session_id).subscribe(
            () => {
                if (this.session.chat_session_id == chat_session_id)
                    this.newChat();
                this.chatService.get_all().subscribe(history => this.history = history);
            }
        );
    }


    selectedFiles: File[] = [];
    uploadProgress: number[] = [];


    changeMessage(index: number) {
        this.newMessage = this.session.history[index].content?.trim() ?? '';
        this.selectedFiles = [];
        this.session.history[index].files?.forEach(file => {
            this.selectedFiles.push(new File([], file.name));
            this.uploadProgress.push(100);
        });
        const newHistory = this.session.history.slice(0, index);
        this.session.history = newHistory;
        this.sessionChanged = true;
    }

    openFileDialog(): void {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.click();
        input.onchange = (event: any) => this.uploadFiles(event.target.files)
    }

    onFileSelected(event: any): void {
        this.uploadFiles(event.target.files);
    }

    onFileDropped(event: DragEvent): void {
        event.preventDefault();
        if (event.dataTransfer?.files)
            this.uploadFiles(event.dataTransfer.files);
    }

    removeFile(index: number): void {
        const fileName = this.selectedFiles[index].name;
        this.chatService.deleteFile(fileName).subscribe(() => this.selectedFiles.splice(index, 1));
        this.uploadProgress.splice(index, 1)
    }

    uploadFiles(files: FileList, index: number = 0, offset: number = -1) {
        if (offset == -1)
            offset = this.selectedFiles.length;
        if (index == 0) {
            this.isUploading$.next(true);
            Array.from(files).forEach(file => this.selectedFiles.push(file));
        }
        if (index >= files.length) {
            this.isUploading$.next(false);
            return;
        }
        const file = files[index];
        const formData = new FormData();
        formData.append('files', file);
        this.chatService.uploadFiles(formData).subscribe({
            next: event => {
                if (event.type === HttpEventType.UploadProgress && event.total) {
                    this.uploadProgress[offset + index] = Math.round(10 * event.loaded / event.total) * 10;
                }
            },
            complete: () => {
                this.uploadProgress[offset + index] = 100;
                this.uploadFiles(files, index + 1, offset);
            }
        });
    }

    async uploadFiles_old() {
        // Upload files to the server
        if (this.selectedFiles.length === 0) {
            return;
        }
        const formData = new FormData();
        for (let i = 0; i < this.selectedFiles.length; i++) {
            formData.append('files', this.selectedFiles[i]);
        }
        await firstValueFrom(this.chatService.uploadFiles(formData));
    }
}