/*Por cada caso a comprobar, recibe tres nombres de archivos como argumento:
argv[1]=input
argv[2]=output esperado
argv[3]=output del programa del competidor
Se debe imprimir en la pantalla el puntaje correspondiente al caso dado (1 o 0)

Compilar con:
gcc -static -o checker checker.cpp
*/
#include <cstdio>
#include <cstdlib>

using namespace std;

int main(int argc, char **argv) {

	FILE *fres = fopen(argv[2], "r");
	FILE *fout = fopen(argv[3], "r");

	int a, b;
	fscanf(fres, "%d", &a);
	fscanf(fout, "%d", &b);


	if (a == b) {
		//lo impreso en stderr aparece en detalles de la submission
		fprintf(stderr, "A-ha, you're the best adding program I've ever met!\n");
		printf("1.0\n");
	} else {
		fprintf(stderr, "How dreadful, never met anyone as dumb as you...\n");
		printf("0.0\n");
	}

	return 0;

}

