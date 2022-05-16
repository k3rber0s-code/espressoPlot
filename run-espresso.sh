#!/bin/bash
# ====================================================
# for running jobs using Espresso
# ====================================================


#PBS -l select=1:ncpus=1:mem=500mb:scratch_local=2gb:cluster=luna
#PBS -l walltime=2:00:00
#PBS -N lj_liquid_tarkil_ema
trap 'clean_scratch' TERM EXIT
trap 'cp -r $SCRATCHDIR/temporary $DATADIR && clean_scratch ' TERM


# DATA
# ====================================================
job_name="lj_liquid"

DATADIR="/storage/vestec1-elixir/home/tomanoem"
cp $DATADIR/$job_name.py $SCRATCHDIR || exit 1
cd $SCRATCHDIR || exit 2
WORKDIR=$job_name
mkdir $WORKDIR

wd="$SCRATCHDIR/$WORKDIR"
cp $job_name.py $wd || exit 2
cd $wd

# VARIBLES
# ======================================================
box_l=15
density=1
kt=1

box_l=$((box_l*2))
density=$((density*2))

# COMPUTATIONAL PART
# ======================================================
module add espresso_md-4.1.4
# mpirun -n 1 pypresso $job_name.py

for i in {1..3}; do
  for j in {1..3}; do
    mpirun -n 1 pypresso $job_name.py $box_l $density $kt
    density=$((density*2))
  done
  box_l=$((box_l*2))
  density=$((density/4))
done

#mpirun -n 1 pypresso $job_name.py $box_l $density $kt

# COPY DATA AND LEAVE
# =======================================================
cd ..
cp -r $WORKDIR $DATADIR || export CLEAN_SCRATCH=false 

exit 0


