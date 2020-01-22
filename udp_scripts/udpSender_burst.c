#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <time.h>
#include <sys/time.h>
#include <limits.h>
#define SERVERPORT "4950"	// the port users will be connecting to
#define BURST_SIZE 6		// Number of packets the script will transmit consecutively
#define SLEEP_BUF 80		// Amount (on average) of microseconds the sleep function adds to sleep time

int send_packets(char *ip, int sleep_rate, int source_rate, FILE *file);

/*
 * Runs the send function with the specified IP address, source rate, and file.
 */
int main(int argc, char *argv[]){
	
    if (argc != 4) {
        fprintf(stderr,"usage: ip source_rate filename\n");
        exit(1);
    }
	
	int rate = 0;
	rate = atoi(argv[2]);
	
	FILE *fp;
	fp = fopen(argv[3],"a");
	
	fprintf(fp,"%d,",rate);
	printf("The source rate is : %d\n", rate);

	// Expected source rates:
	// 1 3 5 6 10 15 25 35 55 70 95 100 200 400 800 1200 1500 1800 3000 4000 6000 8000 10000 12000 14000 16000

	int sleep_rate = 1000000 / rate;
	send_packets(argv[1], sleep_rate, rate, fp);
}

/*
 * Sends a packet to the specified IP address at a specified rate
 * Parameters:
 *   ip -			Pointer to IP address
 *   time -			Wait ime in between every packet sent (microseconds)
 *	 file -			File pointer to where data should be output
 */
int send_packets(char *ip, int sleep_rate, int source_rate, FILE *file)
{
    int sockfd;
    struct addrinfo hints, *servinfo, *p;
    int rv;
    int numbytes;
	int loop;
	int total_packets = source_rate * 10;

    char buf[1470];
    for(int i = 0; i < sizeof(buf); i++){
        buf[i] = 'a';
    }

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_DGRAM;

    if ((rv = getaddrinfo(ip, SERVERPORT, &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 1;
    }

    for(p = servinfo; p != NULL; p = p->ai_next) {
        if ((sockfd = socket(p->ai_family, p->ai_socktype,
                             p->ai_protocol)) == -1) {
            perror("talker: socket");
            continue;
        }

        break;
    }

    if (p == NULL) {
        fprintf(stderr, "talker: failed to create socket\n");
        return 2;
    }
	
	long sndbuf = LONG_MAX;
	int temp = setsockopt(sockfd, SOL_SOCKET,SO_SNDBUF,&sndbuf,sizeof sndbuf);
	// printf("%d\n",temp);



	struct timeval stop, start, current;
	int count = 0;
	long sleep_time = 0;
	
	gettimeofday(&start, NULL);
	//gettimeofday(&total_start, NULL);
	time_t total_time = 0;

	while(total_time < 10){
		gettimeofday(&current, NULL);
		long long cur_time = ((long long)current.tv_sec) * ((long long)1000000) + current.tv_usec;
		// fflush(stdout);
	    if ((numbytes = sendto(sockfd, buf, sizeof(buf), 0,
	                           p->ai_addr, p->ai_addrlen)) == -1) {
	        perror("talker: sendto");
	        exit(1);
	    }
		if(numbytes > 0){
			count = count + 1;
		}
		if(numbytes == 0){
			printf("Send Failed.\n");
			break;
		}

		// fflush(stdout);
		gettimeofday(&current, NULL);
		long long trans_dur = (((long long)current.tv_sec) * ((long long)1000000) + current.tv_usec - cur_time)/2;
		// printf("Trans duration: %lld\n", trans_dur);
		sleep_time = sleep_rate - trans_dur + sleep_time;
		if (count % BURST_SIZE == 0)
		{
			// printf("Packets sent: %d\r",count);
			if (sleep_time < 0) {
				printf("\nSleep calculation is faulty: %ld usecs\n", sleep_time);
				return 1;
			}
			// printf("Sleep Time: %ld\r", sleep_time);
			usleep(sleep_time - SLEEP_BUF);
			sleep_time = 0;
		}

		gettimeofday(&stop, NULL);
		if (count >= total_packets)
		{
			break;
		}
		total_time = stop.tv_sec - start.tv_sec;
	}
    freeaddrinfo(servinfo);

	// The format of the csv file is:
	// (source rate), (start transmission timestamp), (end transmission timestamp), (total transmission time), (sent packet count)
	long long start_time = ((long long)start.tv_sec) * ((long long)1000000) + start.tv_usec;
	long long stop_time = ((long long)stop.tv_sec) * ((long long)1000000) + stop.tv_usec;
	total_time = stop_time - start_time;
	fprintf(file,"%lld,%lld,%ld,%d\n", start_time, stop_time, total_time,count);
	//printf("took %ld, Number of packet is %d \n", total_time, count);
    close(sockfd);

    return 0;
}