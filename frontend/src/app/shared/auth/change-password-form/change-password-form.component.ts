import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { Router, RouterModule } from '@angular/router';
import { passwordStrengthValidator, newPasswordEuqalsValidator, AuthService } from '../auth.service';
import { MainToolbarComponent } from "../../nav/main-toolbar/main-toolbar.component";

@Component({
    selector: 'app-change-password-form',
    standalone: true,
    imports: [
    RouterModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSnackBarModule,
    MainToolbarComponent
],
    templateUrl: './change-password-form.component.html',
    styleUrl: './change-password-form.component.css'
})
export class ChangePasswordFormComponent {

    private readonly fb = inject(FormBuilder)
    form = this.fb.group({
        old_password: ['', Validators.required],
        new_password: ['', [Validators.required, passwordStrengthValidator(8)]],
        new_password2: ['', [Validators.required, newPasswordEuqalsValidator()]],
    })

    constructor(private readonly authService: AuthService) { }

    private readonly snackbar = inject(MatSnackBar);
    private readonly router = inject(Router)

    onSubmit() {
        const formData = this.form.value;
        if (formData.old_password && formData.new_password)
            this.authService.changePassword(formData.old_password, formData.new_password).subscribe({
                complete: () => this.snackbar.open('Hasło zmieniono pomyślnie', 'Zamknij', { duration: 1500 })
                    .afterDismissed().subscribe(() => this.router.navigateByUrl("/")),
                error: (err) => this.snackbar.open(err.error.detail ?? err.message, 'Zamknij')
            })
    }

}
