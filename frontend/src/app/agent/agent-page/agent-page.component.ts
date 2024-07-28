import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MainToolbarComponent } from '../../shared/nav/main-toolbar/main-toolbar.component';

@Component({
    selector: 'app-agent-page',
    standalone: true,
    imports: [RouterOutlet, MainToolbarComponent],
    templateUrl: './agent-page.component.html',
    styleUrl: './agent-page.component.css',
})
export class AgentPageComponent {

    constructor() { }
}

