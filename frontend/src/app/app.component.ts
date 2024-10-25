import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { AuthService } from './shared/auth/auth.service';
import { PingService } from './shared/ping.service';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, RouterOutlet ],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})

export class AppComponent {

    private readonly pingService = inject(PingService)

    constructor(public authService: AuthService) {
    }

}
