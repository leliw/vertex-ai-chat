import { GoogleSigninButtonModule } from '@abacritt/angularx-social-login';
import { Component } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { ConfigService } from '../../config/config.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [MatToolbarModule, GoogleSigninButtonModule],
    templateUrl: './login.component.html',
    styleUrl: './login.component.css'
})
export class LoginComponent {
    version = ""

    constructor(private configService: ConfigService) {
        this.configService.getConfig().subscribe(config => this.version = config.version);
    }
}
