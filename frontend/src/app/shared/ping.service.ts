import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class PingService {

    private pingIntervalId: any = undefined;
    public connected = signal(false);

    constructor(private readonly httpClient: HttpClient) { 
        this.connect('/api/ping');
    }

    connect(endpoint: string = '/api/ping', pingInterval: number = 15000) {
        if (this.pingIntervalId)
            this.disconect();
        this.pingIntervalId = setInterval(
            () => this.httpClient.get<void>(endpoint).subscribe({
                next: () => this.connected.set(true),
                error: () => this.connected.set(false)    
            }),
            pingInterval);
    }

    disconect() {
        clearInterval(this.pingIntervalId);
        this.pingIntervalId = undefined;
    }

}
