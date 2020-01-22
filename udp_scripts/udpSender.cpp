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

int send_packets(char *ip, int src_rate, int sleeptime, FILE *file);

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

	int sleeptime = 1000000 / rate;
	send_packets(argv[1], rate, sleeptime, fp);
}

/*
 * Sends a packet to the specified IP address at a specified rate
 * Parameters:
 *   ip -			Pointer to IP address
 *   time -			Wait ime in between every packet sent (microseconds)
 *	 file -			File pointer to where data should be output
 */
int send_packets(char *ip, int src_rate, int sleeptime, FILE *file)
{
    int sockfd;
    struct addrinfo hints, *servinfo, *p;
    int rv;
    int numbytes;
	int count;

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
	//struct timeval total_stop, total_start;

	gettimeofday(&start, NULL);
	//gettimeofday(&total_start, NULL);
	time_t total_time = 0;

	long long cur_time;
	long long start_time = ((long long)start.tv_sec) * ((long long)1000000) + start.tv_usec;
	bool finished = false;
	int next_transmit = 0;

	printf("Start transmission...");
	while(total_time < 10){
		gettimeofday(&current, NULL);
		cur_time = ((long long)current.tv_sec) * ((long long)1000000) + current.tv_usec;

		long rel_time = cur_time - start_time;
		if (rel_time < next_transmit || finished)
		{
			gettimeofday(&current, NULL);
			long sleep_dur = next_transmit-rel_time;
			if (sleep_dur > 0)
			{
				usleep(sleep_dur);
			}
		}
		else
		{
			fflush(stdout);
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

			fflush(stdout);

			// printf("SENT PACKET %d\n", count);
			next_transmit = next_transmit + sleeptime;
			if (count >= src_rate * 10)
			{
				finished = true;
			}
		}

		gettimeofday(&stop, NULL);
		//gettimeofday(&total_stop, NULL);
		total_time = stop.tv_sec - start.tv_sec;
		// printf("CURRENT TIME: %ld", total_time);
	}
	printf("End transmission\n");
    freeaddrinfo(servinfo);

	// The format of the csv file is:
	// (source rate), (start transmission timestamp), (end transmission timestamp), (total transmission time), (sent packet count)
	long long stop_time = ((long long)stop.tv_sec) * ((long long)1000000) + stop.tv_usec;
	total_time = stop_time - start_time;
	fprintf(file,"%lld,%lld,%ld,%d\n", start_time, stop_time, total_time,count);
	//printf("took %ld, Number of packet is %d \n", total_time, count);
    close(sockfd);

    return 0;
}