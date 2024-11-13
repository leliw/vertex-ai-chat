import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { Router, RouterModule } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService, newPasswordEuqalsValidator, passwordStrengthValidator } from '../auth.service';

@Component({
    selector: 'app-reset-password-form',
    standalone: true,
    imports: [
        RouterModule,
        ReactiveFormsModule,
        MatCardModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatSnackBarModule,
    ],
    templateUrl: './reset-password-form.component.html',
    styleUrl: './reset-password-form.component.css'
})
export class ResetPasswordFormComponent {

    private readonly fb = inject(FormBuilder)
    form = this.fb.group({
        email: ['', [Validators.email, Validators.required]],
        reset_code: ['', Validators.required],
        new_password: ['', [Validators.required, passwordStrengthValidator(8)]],
        new_password2: ['', [Validators.required, newPasswordEuqalsValidator()]],
    })

    constructor(private readonly authService: AuthService) { }

    private readonly snackbar = inject(MatSnackBar);
    private readonly router = inject(Router)

    onSubmit() {
        const formData = this.form.value;
        if (formData.email && formData.reset_code && formData.new_password)
            this.authService.resetPassword(formData.email, formData.reset_code, formData.new_password).subscribe({
                complete: () => this.snackbar.open('Hasło zmieniono pomyślnie', 'Zaloguj', { duration: 1500 })
                    .afterDismissed().subscribe(() => this.router.navigateByUrl("/login")),
                error: (err) => this.snackbar.open(err.error.detail ?? err.message, 'Zamknij')
            })
    }
}