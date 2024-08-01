import { Component, inject } from '@angular/core';

import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatCardModule } from '@angular/material/card';
import { Agent, AgentService } from '../agent.service';
import { ActivatedRoute, Router } from '@angular/router';
import { MatChipInputEvent, MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';


@Component({
    selector: 'app-agent-form',
    templateUrl: './agent-form.component.html',
    // styleUrl: './agent-form.component.css',
    standalone: true,
    imports: [
        ReactiveFormsModule,
        MatCardModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatChipsModule,
    ]
})
export class AgentFormComponent {
    private fb = inject(FormBuilder);
    form = this.fb.group({
        name: ['', Validators.required],
        description: ['', Validators.required],
        model_name: ['', Validators.required],
        system_prompt: ['', Validators.required],
        keywords: [[] as string[]],
    });
    agentName: string = '';
    editMode: boolean = false;

    constructor(private agentService: AgentService, private route: ActivatedRoute,
        private router: Router,) { }

    ngOnInit(): void {
        this.route.params.subscribe(params => {
            if (params['id']) {
                this.agentName = params['id'];
                this.editMode = true;
                this.fetchAgentData(this.agentName);
            }
        });
    }

    fetchAgentData(agentName: string) {
        this.agentService.get(agentName).subscribe({
            next: (agent) => {
                this.form.patchValue(agent);
            },
            error: (error) => {
                console.error('Error fetching agent data:', error);
                // Handle error, e.g., display an error message
            }
        });
    }

    onSubmit(): void {
        if (this.form.invalid) {
            return;
        }
        const formData = this.form.value as Agent;
        if (this.editMode) {
            this.updateAgent(formData);
        } else {
            this.createAgent(formData);
        }
    }

    onCancel(): void {
        this.router.navigate(['/agents']);
    }

    createAgent(agentData: Agent) {
        this.agentService.create(agentData).subscribe({
            next: () => {
                // Handle success, e.g., navigate to the agent list
                this.router.navigate(['/agents']);
            },
            error: (error) => {
                console.error('Error creating agent:', error);
                // Handle error
            }
        });
    }

    updateAgent(agentData: Agent) {
        this.agentService.update(this.agentName, agentData).subscribe({
            next: () => {
                // Handle success, e.g., navigate to the agent list
                this.router.navigate(['/agents']);
            },
            error: (error) => {
                console.error('Error updating agent:', error);
                // Handle error
            }
        });
    }

    addKeyword(event: MatChipInputEvent): void {
        const value = (event.value || '').trim();
        if (value) {
            this.form.get('keywords')?.value?.push(value);
        }
        event.chipInput!.clear();
    }

    removeKeyword(keyword: string): void {
        const keywords = this.form.get('keywords')?.value as string[];
        const index = keywords.indexOf(keyword);
        if (index >= 0) {
            keywords.splice(index, 1);
        }
    }
}

