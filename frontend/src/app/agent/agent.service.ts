import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class AgentService {
    
    private apiUrl = '/api/agents';

    constructor(private http: HttpClient) { }

    get_all(): Observable<string[]> {
        return this.http.get<string[]>(this.apiUrl);
    }

}
