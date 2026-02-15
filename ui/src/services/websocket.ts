import { io, Socket } from 'socket.io-client';
import {
  JobStatusUpdateEvent,
  JobLogEntryEvent,
  JobCompletedEvent,
  JobFailedEvent
} from '@types';

class WebSocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Function[]> = new Map();
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;

  connect(url: string = import.meta.env.VITE_WS_URL || 'http://localhost:8085'): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(url, {
          reconnection: true,
          reconnectionDelay: this.reconnectDelay,
          reconnectionDelayMax: 5000,
          reconnectionAttempts: this.maxReconnectAttempts,
          transports: ['websocket', 'polling']
        });

        this.socket.on('connect', () => {
          console.log('WebSocket connected');
          resolve();
        });

        this.socket.on('disconnect', () => {
          console.log('WebSocket disconnected');
          this.emit('client:disconnected', {});
        });

        this.socket.on('error', (error: any) => {
          console.error('WebSocket error:', error);
          reject(error);
        });

        this.setupEventListeners();
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    // Job status updates
    this.socket.on('job_status_update', (data: any) => {
      this.emit('job_status_update', {
        type: 'job_status_update',
        payload: data,
        timestamp: new Date().toISOString()
      } as JobStatusUpdateEvent);
    });

    // Job log entries
    this.socket.on('job_log_entry', (data: any) => {
      this.emit('job_log_entry', {
        type: 'job_log_entry',
        payload: data,
        timestamp: new Date().toISOString()
      } as JobLogEntryEvent);
    });

    // Job completed
    this.socket.on('job_completed', (data: any) => {
      this.emit('job_completed', {
        type: 'job_completed',
        payload: data,
        timestamp: new Date().toISOString()
      } as JobCompletedEvent);
    });

    // Job failed
    this.socket.on('job_failed', (data: any) => {
      this.emit('job_failed', {
        type: 'job_failed',
        payload: data,
        timestamp: new Date().toISOString()
      } as JobFailedEvent);
    });

    // Queue updates
    this.socket.on('queue_updated', (data: any) => {
      this.emit('queue_updated', {
        type: 'queue_updated',
        payload: data,
        timestamp: new Date().toISOString()
      });
    });
  }

  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  off(event: string, callback: Function): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(cb => cb(data));
    }
  }

  // Send custom events
  sendEvent(event: string, data: any): void {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }

  // Subscribe to job updates
  subscribeToJob(jobId: string): void {
    if (this.socket) {
      this.socket.emit('subscribe_job', { jobId });
    }
  }

  // Unsubscribe from job updates
  unsubscribeFromJob(jobId: string): void {
    if (this.socket) {
      this.socket.emit('unsubscribe_job', { jobId });
    }
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false;
  }
}

export const webSocketService = new WebSocketService();
export default webSocketService;
