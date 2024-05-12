import { GoogleSigninButtonModule } from '@abacritt/angularx-social-login';
import { Component } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [MatToolbarModule, GoogleSigninButtonModule],
    templateUrl: './login.component.html',
    styleUrl: './login.component.css'
})
export class LoginComponent {
    version = "xxx"
}
