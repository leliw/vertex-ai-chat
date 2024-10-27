import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';

@Injectable({
    providedIn: 'root'
})
/**
 * The PingService class is responsible for periodically pinging a specified endpoint to check the connectivity status.
 * It adjusts the ping interval based on the success or failure of the ping requests.
 */
export class PingService {

    /**
     * A signal indicating the connection status.
     * 
     * @type {boolean}
     * @default false
     */
    public connected = signal(false);
    private pingIntervalId: any = undefined;
    private endpoint!: string;
    private pingIntervalOk!: number;
    private pingIntervalFail!: number;

    /**
     * Constructs an instance of PingService.
     * 
     * @param httpClient - The HTTP client used for making HTTP requests.
     */
    constructor(private readonly httpClient: HttpClient) {
        this.init();
    }
    
    
    /**
     * Initializes the ping service with the specified endpoint and intervals.
     *
     * @param {string} [endpoint='/api/ping'] - The endpoint to ping.
     * @param {number} [pingIntervalOk=30000] - The interval in milliseconds to wait between pings when the service is healthy.
     * @param {number} [pingIntervalFail=3000] - The interval in milliseconds to wait between pings when the service is unhealthy.
     */
    init(endpoint: string = '/api/ping', pingIntervalOk: number = 30000, pingIntervalFail: number = 3000) {
        this.endpoint = endpoint;
        this.pingIntervalOk = pingIntervalOk;
        this.pingIntervalFail = pingIntervalFail;
        this.connect(this.pingIntervalFail)
    }

    private connect(pingInterval: number = 15000) {
        if (this.pingIntervalId)
            this.disconect();
        this.pingIntervalId = setInterval(
            () => this.httpClient.get<void>(this.endpoint).subscribe({
                next: () => this.onPingSuccess(),
                error: () => this.onPingError()
            }),
            pingInterval);
    }

    disconect() {
        clearInterval(this.pingIntervalId);
        this.pingIntervalId = undefined;
    }

    private onPingError() {
        console.error('Ping error');
        if (this.connected()) {
            this.connect(this.pingIntervalFail)
            this.connected.set(false);
        }
    }

    private onPingSuccess() {
        if (!this.connected()) {
            this.connect(this.pingIntervalOk)
            this.connected.set(true);
        }
    }
}
