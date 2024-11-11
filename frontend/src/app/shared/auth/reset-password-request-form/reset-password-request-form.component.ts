import { Component, inject } from '@angular/core';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { AuthService } from '../auth.service';
import { Router, RouterModule } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
    selector: 'app-reset-password-request-form',
    standalone: true,
    imports: [
        RouterModule,
        ReactiveFormsModule,
        FormsModule,
        MatCardModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatSnackBarModule,
    ],
    templateUrl: './reset-password-request-form.component.html',
    styleUrl: './reset-password-request-form.component.css'
})
export class ResetPasswordRequestFormComponent {

    fb = inject(FormBuilder);
    form = this.fb.group({
        email: ['', [Validators.email, Validators.required]],
    });

    constructor(private authService: AuthService) { }

    private router = inject(Router);
    private snackbar = inject(MatSnackBar);

    onSubmit() {
        const email = this.form.value.email;
        if (email)
            this.authService.resetPasswordRequest(email).subscribe({
                complete: () => this.snackbar.open(`Kod został wysłany na ${email}`, "Resetuj hasło")
                    .afterDismissed().subscribe(() =>
                        this.router.navigateByUrl("/reset-password")),
                error: (err) => this.snackbar.open(`Bład: ${err.error.detail}`, "Zamknij"),
            })
    }
}