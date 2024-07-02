import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { AuthService } from './shared/auth/auth.service';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, RouterOutlet ],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})

export class AppComponent {

    constructor(public authService: AuthService) {
    }

}
