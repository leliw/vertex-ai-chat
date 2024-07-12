import { Component, inject } from '@angular/core';

import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatCardModule } from '@angular/material/card';
import { Agent, AgentService } from '../agent.service';
import { ActivatedRoute, Router } from '@angular/router';


@Component({
    selector: 'app-agent-form',
    templateUrl: './agent-form.component.html',
    // styleUrl: './agent-form.component.css',
    standalone: true,
    imports: [
        MatInputModule,
        MatButtonModule,
        MatSelectModule,
        MatRadioModule,
        MatCardModule,
        ReactiveFormsModule
    ]
})
export class AgentFormComponent {
    private fb = inject(FormBuilder);
    form = this.fb.group({
        name: ['', Validators.required],
        description: ['', Validators.required],
        model_name: ['', Validators.required],
        system_prompt: ['', Validators.required],
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
                this.form.patchValue({
                    name: agent.name,
                    description: agent.description,
                    model_name: agent.model_name,
                    system_prompt: agent.system_prompt,
                });
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

}

