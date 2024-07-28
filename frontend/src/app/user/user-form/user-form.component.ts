import { Component, inject } from '@angular/core';

import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { User, UserService } from '../user.service';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCheckboxModule } from '@angular/material/checkbox';


@Component({
    selector: 'app-user-form',
    templateUrl: './user-form.component.html',
    standalone: true,
    imports: [
        MatInputModule,
        MatButtonModule,
        MatCheckboxModule,
        MatCardModule,
        ReactiveFormsModule
    ]
})
export class UserFormComponent {
    private fb = inject(FormBuilder);
    form = this.fb.group({
        email: ['', [Validators.required, Validators.email]],
        given_name: ['', Validators.required],
        family_name: ['', Validators.required],
        picture: ['', Validators.required],
        terms_accepted: [false, Validators.required],
    }); 
    email: string = '';
    editMode: boolean = false;

    constructor(private userService: UserService, private route: ActivatedRoute,
        private router: Router,) { }

    ngOnInit(): void {
        this.route.params.subscribe(params => {
            if (params['email']) {
                this.email = params['email'];
                this.editMode = true;
                this.fetchUserData(this.email);
            }
        });
    }

    fetchUserData(email: string) {
        this.userService.getUser(email).subscribe({
            next: (user) => {
                this.form.patchValue(user);
            },
            error: (error) => {
                console.error('Error fetching user data:', error);
                // Handle error, e.g., display an error message
            }
        });
    }

    onSubmit(): void {
        if (this.form.invalid) {
            return;
        }
        const formData = this.form.value as User;
        // formData.id = this.itemId;
        if (this.editMode) {
            this.updateUser(formData);
        } else {
            this.createUser(formData);
        }
    }

    onCancel(): void {
        this.router.navigate(['/users']);
    }

    createUser(userData: User) {
        this.userService.updateUser(userData.email, userData).subscribe({
            next: () => {
                // Handle success, e.g., navigate to the item list
                this.router.navigate(['/users']);
            },
            error: (error) => {
                console.error('Error creating user:', error);
                // Handle error
            }
        });
    }

    updateUser(userData: User) {
        this.userService.updateUser(this.email, userData).subscribe({
            next: () => {
                // Handle success, e.g., navigate to the item list
                this.router.navigate(['/users']);
            },
            error: (error) => {
                console.error('Error updating user:', error);
                // Handle error
            }
        });
    }

}

