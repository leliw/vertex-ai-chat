import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MainToolbarComponent } from '../../shared/nav/main-toolbar/main-toolbar.component';

@Component({
    selector: 'app-user-page',
    standalone: true,
    imports: [RouterOutlet, MainToolbarComponent],
    templateUrl: './user-page.component.html',
})
export class UserPageComponent {

    constructor() { }

}

