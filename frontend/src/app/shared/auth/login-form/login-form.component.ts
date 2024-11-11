import { Component, OnInit } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../auth.service';
import { MatCheckboxModule } from '@angular/material/checkbox';

@Component({
    selector: 'app-login-form',
    standalone: true,
    imports: [
        RouterModule,
        FormsModule,
        ReactiveFormsModule,
        MatCardModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatCheckboxModule
    ],
    templateUrl: './login-form.component.html',
    styleUrl: './login-form.component.css'
})
export class LoginFormComponent implements OnInit {
    credentials = { username: '', password: '', store_token: false };

    constructor(private readonly authService: AuthService, private readonly router: Router) {
    }

    ngOnInit() {
        if (this.authService.isLoggedIn())
            this.router.navigate(['/']);
    }

    onSubmit() {
        this.authService.login(this.credentials).subscribe();
    }

}