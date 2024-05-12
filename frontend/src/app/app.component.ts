import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { AuthService } from './shared/auth/auth.service';
import { LoginComponent } from './shared/login/login.component';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, RouterOutlet, LoginComponent ],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})

export class AppComponent {

    constructor(public authService: AuthService) {
    }

}
