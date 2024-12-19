import { Component, inject } from '@angular/core';
import { FormBuilder, Validators, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../shared/auth/auth.service';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { ApiService, ApiUser } from '../shared/api.service';
import { GoogleAuthService } from '../shared/auth/google-auth.service';

@Component({
    selector: 'app-register',
    standalone: true,
    imports: [
        RouterModule,
        ReactiveFormsModule,
        MatFormFieldModule, FormsModule,
        MatInputModule, MatCheckboxModule, MatButtonModule,
        MatCardModule
    ],
    templateUrl: './register.component.html',
    styleUrl: './register.component.css'
})
export class RegisterComponent {
    private fb = inject(FormBuilder);
    form = this.fb.group({
        email: ['', [Validators.required, Validators.email]],
        firstName: ['', Validators.required],
        lastName: ['', Validators.required],
        termsAccepted: [false, Validators.requiredTrue],
    });

    constructor(
        public googleAuthService: GoogleAuthService,
        private router: Router,
        private snackBar: MatSnackBar,
        private apiService: ApiService,
    ) {
        this.form.patchValue({
            email: googleAuthService.user?.email ?? '',
            // name: authService.socialUser?.name ?? '',
            firstName: googleAuthService.user?.firstName ?? '',
            lastName: googleAuthService.user?.lastName ?? '',
        });
    }

    onCancel() {
        this.router.navigate(['/login']);
    }

    onSubmit() {
        if (this.form.valid) {
            const formData = this.form.value as unknown as ApiUser;
            // Register user
            this.apiService.register(formData)
                .subscribe({
                    next: (user) => {
                        // If user is already authorized with google
                        if (this.googleAuthService.user) {
                            // Get tokens for google user
                            this.googleAuthService.getTokens(this.googleAuthService.user).subscribe(() =>
                                this.snackBar.open('Rejestracja udana! ', 'Zamknij', { duration: 5000 }).afterDismissed().subscribe(() =>
                                    this.router.navigate(['/']))
                            );
                        } else {
                            this.snackBar.open('Rejestracja udana! Skorzystaj z żądania resetowania hasła, aby ustawić hasło.', 'Zamknij', { duration: 5000 })
                                .afterDismissed().subscribe(() => {
                                    this.router.navigate(['/reset-password-request']);
                                });
                        }
                    },
                    error: (error) => {
                        console.error('Błąd rejestracji:', error);
                        this.snackBar.open(error.error.message ?? error.error.detail, 'Zamknij');
                    }
                });
        }
    }
}