import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
    selector: 'app-terms-of-service',
    standalone: true,
    imports: [RouterModule],
    templateUrl: './terms-of-service.component.html',
    styleUrl: './terms-of-service.component.css'
})
export class TermsOfServiceComponent {
    url = "https://ai-chat.leliwa.priv.pl";
}
