import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Agent {
    name: string;
    description: string;
    ai_model_name: string;
    system_prompt: string;
    keywords: string[];
}

@Injectable({
    providedIn: 'root'
})
export class AgentService {
    
    private apiUrl = '/api/agents';

    constructor(private http: HttpClient) { }

    get_all(): Observable<Agent[]> {
        return this.http.get<Agent[]>(this.apiUrl);
    }

    get(agentName: string): Observable<Agent> {
        return this.http.get<Agent>(`${this.apiUrl}/${agentName}`);
    }

    create(agent: Agent): Observable<Agent> {
        return this.http.post<Agent>(this.apiUrl, agent);
    }

    update(agentName: string, agent: Agent): Observable<Agent> {
        return this.http.put<Agent>(`${this.apiUrl}/${agentName}`, agent);
    }

    delete(agentName: string): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/${agentName}`);
    }

}

