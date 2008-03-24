#include <ctype.h>
#include <malloc.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#define G 16 /* number of games */
#define MIN_TO_QUALIFY 0.7 /* minimum percentage of rounds played to qualify for averages.txt*/

typedef struct
{
	short home;
	short away;
} game;

typedef struct
{
	char name[30+1];
	game prediction[G];
} pl;

typedef struct
{
	char name[30+1];
	int points;
	short spotOn;
	short roundsPlayed;
} tab;

int main()
{
	pl player;
	game result;
	char choice;
	char game[35+1], name[30+1];
	char *line;
	char *line2;
	int i, j, totalPoints, totalPointsAll, size;
	int points[G], gameTotalPoints[G], temp;
	int sortGameTotalPoints[G], gamesPlayed;
	short numberOfPlayers, spotOn, rounds;
	tab sort[30], oldData, newData;
	tab *sortStandings;
	float avgi, avgj;

	FILE *averages;      /* averages */
	FILE *database;      /* database */
	FILE *games;         /* fixtures */
	FILE *new_standings; /* new overall standings */
	FILE *predictions;   /* predictions */
	FILE *results;       /* game results */
	FILE *standings;     /* overall standings */
	FILE *stats;         /* game predictability */
	FILE *table;         /* results for the current round */

	while (choice != 'Q')
	{
		printf("\na) Add new prediction\n");
		printf("b) Print predictions\n");
		printf("c) Change prediction\n");
		printf("d) Enter results\n");
		printf("e) Print results\n");
		printf("f) Change result\n");
		printf("g) Calculate points and save stats.txt and table.txt\n");
		printf("h) Update standings, database & averages (only after g) !)\n");
		printf("i) Print database\n");
		printf("q) Quit\n");
		choice = toupper(getchar());
		getchar();

		switch (choice)
		{
			case 'A': /* Add new prediction */
				printf("\nName: ");
				gets (player.name);
				games = fopen("games.txt", "r");
				for (i=0; i<G; i++)
				{
					fgets(game, 35, games);
					printf("Game %2d: %s", i, game);
					printf("Home goals: ");
					scanf("%hd", &player.prediction[i].home);
					printf("Away goals: ");
					scanf("%hd", &player.prediction[i].away);
				}
				fclose(games);
				predictions = fopen("predictions.txt", "a");
				fwrite(&player, sizeof(player), 1, predictions);
				fclose(predictions);
				getchar();
				break;
			case 'B': /* Print predictions */
				if ((predictions = fopen("predictions.txt", "r")) == NULL)
				{
					printf("Predictions.txt doesn't exist!\n");
					break;
				}
				games = fopen("games.txt", "r");
				while (fread(&player, sizeof(player), 1, predictions))
				{
					printf("Name: %-30s\n", player.name);
					for (i=0; i<G; i++)
					{
						fgets(game, 35, games);
						size = strlen(game);
						game[size-1] = '\0';
						printf("%2d. %-35s %hd - %hd\n", i+1, game, player.prediction[i].home, player.prediction[i].away);
					}
					fseek(games, 0L, SEEK_SET);
					printf("\nPress <ENTER> to continue...\n");
					getchar();
				}
				fclose(games);
				fclose(predictions);
				break;
			case 'C': /* Change prediction */
				if ((predictions = fopen("predictions.txt", "r+")) == NULL)
				{
					printf("Predictions.txt doesn't exist!\n");
					break;
				}
				j = 0;
				temp = 0;
				printf("Name: ");
				gets(name);
				while (fread(&player, sizeof(player), 1, predictions))
				{
					if (!strcmp(name, player.name))
					{
						temp = 1;
						break;
					}
					j++;
				}
				if (temp == 1)
				{
					games = fopen("games.txt", "r");
					printf("Name: %-30s\n", player.name);
					for (i=0; i<G; i++)
					{
						fgets(game, 35, games);
						size = strlen(game);
						game[size-1] = '\0';
						printf("%2d. %-35s %hd - %hd\n", i+1, game, player.prediction[i].home, player.prediction[i].away);
					}
					printf("Prediction to change: ");
					scanf("%d", &temp);
					fseek(games, 0L, SEEK_SET);
					for (i=0; i<temp; i++)
						fgets(game, 35, games);
					size = strlen(game);
					game[size-1] = '\0';
					printf("Old prediction: %-35s %hd - %hd\n", game, player.prediction[temp-1].home, player.prediction[temp-1].away);
					printf("New prediction:\n");
					printf("Home goals: ");
					scanf("%hd", &player.prediction[temp-1].home);
					printf("Away goals: ");
					scanf("%hd", &player.prediction[temp-1].away);
					fseek(predictions, j*sizeof(player), SEEK_SET);
					fwrite(&player, sizeof(player), 1, predictions);
					fseek(games, 0L, SEEK_SET);
					for (i=0; i<G; i++)
					{
						fgets(game, 35, games);
						size = strlen(game);
						game[size-1] = '\0';
						printf("%2d. %-35s %hd - %hd\n", i+1, game, player.prediction[i].home, player.prediction[i].away);
					}
					fclose(games);
					getchar();
				}
				else
					printf("Name not found!\n");
				fclose(predictions);
				getchar();
				break;
			case 'D': /* Enter results */
				results = fopen("results.txt", "w");
				games = fopen("games.txt", "r");
				for (i=0; i<G; i++)
				{
					fgets(game, 35, games);
					printf("\nGame %2d: %s", i, game);
					printf("Home goals: ");
					scanf("%hd", &result.home);
					printf("Away goals: ");
					scanf("%hd", &result.away);
					fwrite(&result, sizeof(result), 1, results);
				}
				fclose(games);
				fclose(results);
				getchar();
				break;
			case 'E': /* Print results */
				i=0;
				if ((results = fopen("results.txt", "r")) == NULL)
				{
					printf("Results.txt doesn't exist!\n");
					break;
				}
				games = fopen("games.txt", "r");
				printf(" * * * * * RESULTS * * * * *\n\n");
				while (fread(&result, sizeof(result), 1, results))
				{
					i++;
					fgets(game, 35, games);
					size = strlen(game);
					game[size-1] = '\0';
					printf("%2d. %-35s %hd - %hd\n", i, game, result.home, result.away);
				}
				fclose(games);
				fclose(results);
				getchar();
				break;
			case 'F': /* Change result */
				i = 0;
				if ((results = fopen("results.txt", "r+")) == NULL)
				{
					printf("Results.txt doesn't exist!\n");
					break;
				}
				games = fopen("games.txt", "r");
				while (fread(&result, sizeof(result), 1, results))
				{
					i++;
					fgets(game, 35, games);
					size = strlen(game);
					game[size-1] = '\0';
					printf("%2d. %-35s %hd - %hd\n", i, game, result.home, result.away);
				}
				fseek(results, 0L, SEEK_SET);
				printf("Result to change: ");
				scanf("%d", &temp);
				for (i=0; i < temp; i++)
					fread(&result, sizeof(result), 1, results);
				printf("Old result: %hd - %hd\n", result.home, result.away);
				printf("New result:\n");
				printf("Home goals: ");
				scanf("%hd", &result.home);
				printf("Away goals: ");
				scanf("%hd", &result.away);
				fseek(results, 0L, SEEK_SET);
				fseek(results, (temp-1)*sizeof(result), SEEK_SET);
				fwrite(&result, sizeof(result), 1, results);
				i = 0;
				fseek(results, 0L, SEEK_SET);
				fseek(games, 0L, SEEK_SET);
				while (fread(&result, sizeof(result), 1, results))
				{
					i++;
					fgets(game, 35, games);
					size = strlen(game);
					game[size-1] = '\0';
					printf("%2d. %-35s %hd - %hd\n", i, game, result.home, result.away);
				}
				fclose(games);
				fclose(results);
				getchar();
				getchar();
				break;
			case 'G': /* Calculate points */
				if ((results = fopen("results.txt", "r")) == NULL)
				{
					printf("Results.txt doesn't exist!\n");
					break;
				}
				if ((predictions = fopen("predictions.txt", "r+")) == NULL)
				{
					printf("Predictions.txt doesn't exist!\n");
					break;
				}
				for (i=0; i<G; i++)
				{
					sortGameTotalPoints[i] = i;
					gameTotalPoints[i] = 0;
				}
				numberOfPlayers = 0;
				totalPointsAll = 0;
				gamesPlayed = 0;
				while (fread(&player, sizeof(player), 1, predictions))
				{
					numberOfPlayers++;
					totalPoints = 0;
					spotOn = 0;
					fseek(results, 0L, SEEK_SET);
					printf("%-30s", player.name);
					for (i=0; i<G; i++)
					{
						fread(&result, sizeof(result), 1, results);
						/* game wasn't played (9 - 9) = 0 points */
						if (result.home == 9 && result.away == 9)
						{
							temp = 0;
							gameTotalPoints[i] += 0;
						}
						/* no prediction (9 - 9) = 0 points */
						else if (player.prediction[i].home == 9 && player.prediction[i].away == 9)
						{
							temp = 0;
							gameTotalPoints[i] += 0;
						}
						/* correct result = 4 points */
						else if (result.home == player.prediction[i].home && result.away == player.prediction[i].away)
						{
							temp = 4;
							gameTotalPoints[i] += 4;
							spotOn++;
						}
						/* draw */
						else if (result.home == result.away && player.prediction[i].home == player.prediction[i].away)
						{
							/* missed by 1 = 3 points */
							if (abs(result.home - player.prediction[i].home) == 1)
							{
								temp = 3;
								gameTotalPoints[i] += 3;
							}
							/* missed by more than 1 = 2 points */
							else
							{
								temp = 2;
								gameTotalPoints[i] += 2;
							}
						}
						/* win - correct goal difference = 3 points */
						else if ((result.home - result.away) == (player.prediction[i].home - player.prediction[i].away))
						{
							temp = 3;
							gameTotalPoints[i] += 3;
						}
						/* away win = 2 points */
						else if (result.home < result.away && player.prediction[i].home < player.prediction[i].away)
						{
							temp = 2;
							gameTotalPoints[i] += 2;
						}
						/* home win = 2 points */
						else if (result.home > result.away && player.prediction[i].home > player.prediction[i].away)
						{
							temp = 2;
							gameTotalPoints[i] += 2;
						}
						/* miss = 0 points */
						else
							temp = 0;
						printf("%d ", temp);
						totalPoints += temp;
					}
					printf("%2d %2hd\n", totalPoints, spotOn);
					totalPointsAll += totalPoints;
					strcpy(sort[numberOfPlayers-1].name, player.name);
					sort[numberOfPlayers-1].points = totalPoints;
					sort[numberOfPlayers-1].spotOn = spotOn;
				}
				fclose(results);
				fclose(predictions);
				for (i=0; i<G; i++)
					points[i] = gameTotalPoints[i];
				printf("Press <ENTER> to countinue...\n");
				getchar();
				printf(" * * * * * GAME STATS * * * * *\n\n");
				printf("Total points scored = %3d  Players = %2hd  Avg = %f\n", totalPointsAll, numberOfPlayers, ((float) totalPointsAll)/numberOfPlayers);
				/* sorting stats.txt */
				for (i=0; i < G; i++)
				{
					for (j=i; j<G; j++)
					{
						if (points[i] < points[j])
						{
							temp = points[i];
							points[i] = points[j];
							points[j] = temp;
							temp = sortGameTotalPoints[i];
							sortGameTotalPoints[i] = sortGameTotalPoints[j];
							sortGameTotalPoints[j] = temp;
						}
					}
				}
				/* sorting table.txt */
				for (i=0; i < numberOfPlayers; i++)
				{
					for (j=i; j < numberOfPlayers; j++)
					{
						if (sort[i].points < sort[j].points)
						{
							sort[numberOfPlayers] = sort[i];
							sort[i] = sort[j];
							sort[j] = sort[numberOfPlayers];
						}
						if (sort[i].points == sort[j].points)
						{
							if (sort[i].spotOn < sort[j].spotOn)
							{
								sort[numberOfPlayers] = sort[i];
								sort[i] = sort[j];
								sort[j] = sort[numberOfPlayers];
							}
						}
					}
				}
				/* creating table.txt */
				table = fopen("table.txt", "w");
				fprintf(table, "    Competitor:                   Pts: Res:\n");
				for (i=0; i<numberOfPlayers; i++)
					fprintf(table, "%2d. %-30s %2d  %2hd\n", i+1, sort[i].name, sort[i].points, sort[i].spotOn);
				fclose(table);
				games = fopen("games.txt", "r");
				stats = fopen("stats.txt", "w");
				results = fopen("results.txt", "r");
				/* creating stats.txt */
				fprintf(stats, "    Game:                               Result: Pts:   Avg:\n");
				for (i=0; i < G; i++)
				{
					j=0;
					fseek(games, 0L, SEEK_SET);
					temp = sortGameTotalPoints[i];
					fseek(results, temp*sizeof(result), SEEK_SET);
					fread(&result, sizeof(result), 1, results);
					if (result.home != 9 && result.away != 9)
						gamesPlayed++;
					do
					{
						fgets(game, 35, games);
						j++;
					} while (j <= temp);
					size = strlen(game);
					game[size-1] = '\0';
					printf("Game %2d: %-35s Total = %2d  Avg = %f %d\n", i, game, gameTotalPoints[temp], ((float) gameTotalPoints[temp])/numberOfPlayers, temp);
					if (result.home == 9 && result.away == 9)
						fprintf(stats, "%2d. %-35s  - - -   %2d   %.3f\n", i+1, game, gameTotalPoints[temp], ((float) gameTotalPoints[temp])/numberOfPlayers);
					else
						fprintf(stats, "%2d. %-35s  %hd - %hd   %2d   %.3f\n", i+1, game, result.home, result.away, gameTotalPoints[temp], ((float) gameTotalPoints[temp])/numberOfPlayers);
				}
				fclose(results);
				fclose(games);
				fprintf(stats, "\nCompetitors = %2hd\n", numberOfPlayers);
				fprintf(stats, "Total points scored = %2d\n", totalPointsAll);
				fprintf(stats, "Average points scored = %.3f\n", ((float) totalPointsAll) / numberOfPlayers);
				fprintf(stats, "Average points per game = %.3f", ((float) totalPointsAll) / (numberOfPlayers * gamesPlayed));
				fclose(stats);
				getchar();
				break;
			case 'H': /* Update standings, database & averages */
				if ((table = fopen("table.txt", "r")) == NULL)
				{
					printf("Table.txt doesn't exist!\n");
					break;
				}
				if ((database = fopen("database.txt", "r+b")) == NULL)
					database = fopen("database.txt", "w+b");
				line = (char *)malloc(80*sizeof(char));
				fgets(line, 80, table);
				free(line);
				printf("Reading data...\n");
				while (fscanf(table, "%2d. ", &i) == 1)
				{
					fgets(newData.name, 31, table);
					fscanf(table, " %2d   %2hd\n", &newData.points, &newData.spotOn);
					printf("%2d. %-30s %2d  %2hd", i, newData.name, newData.points, newData.spotOn);
					i = 0;
					for (j=29; j>0; j--)
					{
						if (newData.name[j] == ' ')
							newData.name[j] = '\0';
						else
							break;
					}
					temp = 0;
					fseek(database, 0L, SEEK_SET);
					while (fread(&oldData, sizeof(oldData), 1, database))
					{
						i++;
						if (!strcmp(oldData.name, newData.name))
						{
							temp = 1;
							i--;
							break;
						}
					}
					printf("\n%d %d %d ", strlen(oldData.name), strlen(newData.name), i);
					fseek(database, i*sizeof(newData), SEEK_SET);
					fread(&oldData, sizeof(oldData), 1, database);
					if (temp == 0)
					{
						oldData.points = 0;
						oldData.spotOn = 0;
						oldData.roundsPlayed = 0;
					}
					newData.points += oldData.points;
					newData.spotOn += oldData.spotOn;
					newData.roundsPlayed = oldData.roundsPlayed + 1;
					fseek(database, i*sizeof(newData), SEEK_SET);
					fwrite(&newData, sizeof(newData), 1, database);
				}
				fclose(table);
				numberOfPlayers = 0;
				rounds = 0;
				fseek(database, 0L, SEEK_SET);
				while (fread(&oldData, sizeof(oldData), 1, database))
				{
					numberOfPlayers++;
					if (oldData.roundsPlayed > rounds)
						rounds = oldData.roundsPlayed;
				}
				sortStandings = (tab *)malloc(numberOfPlayers*sizeof(oldData));
				fseek(database, 0L, SEEK_SET);
				for (i=0; i<numberOfPlayers; i++)
				{
					fread(&newData, sizeof(newData), 1, database);
					sortStandings[i] = newData;
				}
				fclose(database);
				/* sorting standings.txt */
				printf("Sorting standings...\n");
				for (i=0; i<numberOfPlayers; i++)
				{
					for (j=i; j<numberOfPlayers; j++)
					{
						if (sortStandings[i].points < sortStandings[j].points)
						{
							oldData = sortStandings[i];
							sortStandings[i] = sortStandings[j];
							sortStandings[j] = oldData;
						}
						if (sortStandings[i].points == sortStandings[j].points)
						{
							if (sortStandings[i].spotOn < sortStandings[j].spotOn)
							{
								oldData = sortStandings[i];
								sortStandings[i] = sortStandings[j];
								sortStandings[j] = oldData;
							}
						}
					}
				}
				/* creating standings.txt */
				printf("Creating standings.txt\n");
				new_standings = fopen("new_standings.txt", "w");
				if ((standings = fopen("standings.txt", "r")) == NULL)
					standings = fopen("standings.txt", "w+");
				fprintf(new_standings, "          Competitor:                    Pts: Res:\n");
				line = (char *)malloc(80*sizeof(char));
				line2 = (char *)malloc(7*sizeof(char));
				for (i=0; i<numberOfPlayers; i++)
				{
					temp = 0;
					fseek(standings, 0L, SEEK_SET);
					fgets(line, 80, standings);
					while (fscanf(standings, "%2d. ", &newData.points) == 1) // newData.points is the old position
					{
						fgets(line2, 7, standings);
						fgets(newData.name, 31, standings);
						for (j=29; j>0; j--)
						{
							if (newData.name[j] == ' ')
								newData.name[j] = '\0';
							else
								break;
						}
						if (!strcmp(newData.name, sortStandings[i].name))
						{
							temp = 1;
							j = newData.points - i - 1;
							break;
						}
						fgets(line, 15, standings);
					}
					if (temp)
						if (j != 0)
							fprintf(new_standings, "%2d. (%+3d) %-30s %3d   %2hd\n", i+1, j, sortStandings[i].name, sortStandings[i].points, sortStandings[i].spotOn);
						else
							fprintf(new_standings, "%2d. ( - ) %-30s %3d   %2hd\n", i+1, sortStandings[i].name, sortStandings[i].points, sortStandings[i].spotOn);
					else
						fprintf(new_standings, "%2d. (new) %-30s %3d   %2hd\n", i+1, sortStandings[i].name, sortStandings[i].points, sortStandings[i].spotOn);
				}
				free(line);
				free(line2);
				fclose(standings);
				fclose(new_standings);
				remove("standings.txt");
				rename("new_standings.txt", "standings.txt");
				/* sorting averages */
				printf("Sorting averages...\n");
				for (i=0; i<numberOfPlayers; i++)
				{
					for (j=i; j<numberOfPlayers; j++)
					{
						avgi = (float) sortStandings[i].points / sortStandings[i].roundsPlayed;
						avgj = (float) sortStandings[j].points / sortStandings[j].roundsPlayed;
						if (avgi < avgj)
						{
							oldData = sortStandings[i];
							sortStandings[i] = sortStandings[j];
							sortStandings[j] = oldData;
						}
						else if (avgi == avgj)
						{
							if (sortStandings[i].points < sortStandings[j].points)
							{
								oldData = sortStandings[i];
								sortStandings[i] = sortStandings[j];
								sortStandings[j] = oldData;
							}
							else if (sortStandings[i].points == sortStandings[j].points)
								if (sortStandings[i].spotOn < sortStandings[j].spotOn)
								{
									oldData = sortStandings[i];
									sortStandings[i] = sortStandings[j];
									sortStandings[j] = oldData;
								}
						}
					}
				}
				/* creating averages.txt */
				printf("Creating averages.txt\n");
				averages = fopen("averages.txt", "w");
				fprintf(averages, "To qualify: %2.f%% (%hd/%hd)\n\n", MIN_TO_QUALIFY * 100, (short)ceil(rounds*MIN_TO_QUALIFY), rounds);
				fprintf(averages, "Qualified:\n\n");
				fprintf(averages, "    Competitor:                     Avg:   Rnds:\n");
				for (i=0, j=0; i<numberOfPlayers; i++)
				{
					if (sortStandings[i].roundsPlayed > (short)floor(rounds * MIN_TO_QUALIFY))
					{
						j++;
						fprintf(averages, "%2d. %-30s %6.3f   %2hd\n", j, sortStandings[i].name, (float) sortStandings[i].points / sortStandings[i].roundsPlayed, sortStandings[i].roundsPlayed);
					}
				}
				fprintf(averages, "\n");
				fprintf(averages, "Did not qualify:\n\n");
				fprintf(averages, "    Competitor:                     Avg:   Rnds:\n");
				for (i=0; i<numberOfPlayers; i++)
				{
					if (sortStandings[i].roundsPlayed <= (short)floor(rounds * MIN_TO_QUALIFY))
					{
						j++;
						fprintf(averages, "%2d. %-30s %6.3f   %2hd\n", j, sortStandings[i].name, (float) sortStandings[i].points / sortStandings[i].roundsPlayed, sortStandings[i].roundsPlayed);
					}
				}
				fclose(averages);
				free(sortStandings);
				printf("Done. Press <ENTER> to continue\n");
				getchar();
				break;
			case 'I': /* Print database */
				if ((database = fopen("database.txt", "r")) == NULL)
				{
					printf("Database.txt doesn't exist!\n");
					break;
				}
				fseek(database, 0L, SEEK_SET);
				while (fread(&newData, sizeof(newData), 1, database))
					printf("%-30s %3d %2hd %2hd %6.3f\n", newData.name, newData.points, newData.spotOn, newData.roundsPlayed, (float)newData.points/newData.roundsPlayed);
				getchar();
				break;
			case 'Q': /* Quit */
				break;
			default:
				printf("Wrong key. Try again\n");
				break;
		}
	}
	return 0;
}