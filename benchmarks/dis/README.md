# DIS Benchmarks

## Compiling Pythia

```
g++ src/pythia_dis.cc -o pythia_dis  \
   -I/home/whit/stow/hepmc3/include  \
   -I../include -O2 -std=c++11 -pedantic -W -Wall -Wshadow -fPIC  \
   -L../lib -Wl,-rpath,../lib -lpythia8 -ldl \
   -L/home/whit/stow/hepmc3/lib -Wl,-rpath,/home/whit/stow/hepmc3/lib -lHepMC3
```

