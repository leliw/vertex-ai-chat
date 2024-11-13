import { Component, inject, OnInit } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../auth.service';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ConfigService } from '../../config/config.service';

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
        MatCheckboxModule,
        MatSnackBarModule,
    ],
    templateUrl: './login-form.component.html',
    styleUrl: './login-form.component.css'
})
export class LoginFormComponent implements OnInit {
    credentials = { username: '', password: '', store_token: false };
    version = ""

    constructor(private readonly authService: AuthService, private readonly router: Router, private configService: ConfigService) {
        this.configService.getConfig().subscribe(config => this.version = config.version);
    }

    ngOnInit() {
        if (this.authService.isLoggedIn())
            this.router.navigate(['/']);
    }

    snackbar = inject(MatSnackBar);

    onSubmit() {
        this.authService.login(this.credentials).subscribe({
            complete: () => { },
            error: (err) => this.snackbar.open(err.error.detail ?? err.message, 'Zamknij')
        });
    }

}