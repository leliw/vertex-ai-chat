import { Component, inject } from '@angular/core';
import { FormBuilder, Validators, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../shared/auth/auth.service';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { ApiService, ApiUser } from '../shared/api.service';

@Component({
    selector: 'app-register',
    standalone: true,
    imports: [
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
        name: [''],
        firstName: ['', Validators.required],
        lastName: ['', Validators.required],
        termsAccepted: [false, Validators.requiredTrue],
    });

    constructor(
        private authService: AuthService,
        private router: Router,
        private snackBar: MatSnackBar,
        private apiService: ApiService,
    ) {
        this.form.patchValue({
            email: authService.socialUser?.email ?? '',
            name: authService.socialUser?.name ?? '',
            firstName: authService.socialUser?.firstName ?? '',
            lastName: authService.socialUser?.lastName ?? '',
        });
    }

    onCancel() {
        this.router.navigate(['/login']);
    }

    onSubmit() {
        if (this.form.valid) {
            const formData = this.form.value as unknown as ApiUser;

            this.apiService.register(formData)
                .subscribe({
                    next: (user) => {
                        this.snackBar.open('Rejestracja udana! Zaloguj się.', 'Zamknij');
                        this.router.navigate(['/login']);
                    },
                    error: (error) => {
                        this.snackBar.open(error.error.message, 'Zamknij');
                    }
                });
        }
    }
}