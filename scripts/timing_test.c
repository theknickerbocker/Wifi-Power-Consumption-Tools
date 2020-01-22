#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/time.h>

int main(int argc, char *argv[]){
	struct timeval stop, start, mid;
    struct timespec sleep_time;

    sleep_time.tv_sec = 0;
    sleep_time.tv_nsec = 50000L;

    gettimeofday(&start, NULL);
    nanosleep(&sleep_time, NULL);
    gettimeofday(&stop, NULL);

    long long start_time = ((long long)start.tv_sec) * ((long long)1000000) + start.tv_usec;
    long long stop_time = ((long long)stop.tv_sec) * ((long long)1000000) + stop.tv_usec;

    long duration = stop_time - start_time;

    printf("TIME SLEPT: %ld\n", duration);

    gettimeofday(&start, NULL);
    gettimeofday(&mid, NULL);
    gettimeofday(&stop, NULL);

    start_time = ((long long)start.tv_sec) * ((long long)1000000) + start.tv_usec;
    stop_time = ((long long)stop.tv_sec) * ((long long)1000000) + stop.tv_usec;

    duration = stop_time - start_time;

    printf("TIME CALL DUR: %ld\n", duration);
}