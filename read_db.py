from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base



engine = create_engine('mysql://anonymous@ensembldb.ensembl.org:3306/ensembl_metadata_104', echo = True)
Base = declarative_base()

app = Flask(__name__)

# the name of the database; add path if necessary

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://anonymous@ensembldb.ensembl.org:3306/ensembl_metadata_104'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


class Organism(Base):
    __tablename__ = 'organism'
    organism_id = Column(Integer, primary_key=True)
    name = Column(String)

class Genome(Base):
    __tablename__ = 'genome'
    genome_id = Column(Integer, primary_key=True)
    organism_id = Column(Integer)
    data_release_id = Column(Integer)

class GenomeDB(Base):
    __tablename__ = 'genome_database'
    genome_database_id = Column(Integer, primary_key=True)
    genome_id = Column(Integer)
    dbname = Column(String)
    type = Column(String)

class DataRelease(Base):
    __tablename__ = 'data_release'
    data_release_id = Column(Integer, primary_key=True)
    ensembl_version = Column(Integer)
    ensembl_genomes_version = Column(Integer)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind = engine)
session = Session()


def parse(my_species = "homo_sapiens", my_version = 100):

    result = session.query(
        Organism, Genome, GenomeDB, DataRelease,
    ).filter(
        Organism.organism_id == Genome.organism_id,
    ).filter(
        GenomeDB.genome_id == Genome.genome_id,
    ).filter(
        DataRelease.data_release_id == Genome.data_release_id,
    ).filter(
        Organism.name == my_species,
    ).filter(
        DataRelease.ensembl_version == my_version,
    ).all()

    my_list = list()

    for row in result:

        my_list.append({"dbname" : "_".join([row[0].name,row[2].type,str(row[3].ensembl_version),str(row[3].ensembl_genomes_version)]), "type" : row[2].type})

    return my_list




@app.route('/')
def index():
  return render_template('index.html')



@app.route('/results',methods = ['GET', 'POST'])
def resultat():
  result = request.args
  n = result['species']
  p = result['release']

  my_list = parse(n, p)

  return render_template("results.html", my_list=my_list)


if __name__ == '__main__':
    app.run(debug=True)
