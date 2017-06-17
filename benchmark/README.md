# benchmarks

## benchsimple
In the subfolder [benchsimple/](benchmark/benchsimple/), there is a configuration file [config_pystpl.py](benchmark/benchsimple/config_pystpl.py) for the **benchsimple** template engine benchmark (see [https://www.simple-is-better.org/template/#benchsimple](https://www.simple-is-better.org/template/#benchsimple)).

Run the benchmark via

    cd benchmark/benchsimple
    python benchsimple.py pystpl

Result in comparison with other template engines

    pystpl 0.0.1
    -------
      import:       10.4709 ms
      complete:      3.7436 ms
      parse only:    0.4104 ms
      render only:   3.2643 ms

    Cheetah ?.?
    -------
      import:       80.0281 ms
      complete:      2.2945 ms
      parse only:    0.0251 ms
      render only:   2.2269 ms
    
    
    mako 1.0.6
    -------
      import:       92.7191 ms
      complete:      5.8826 ms
      parse only:    5.6144 ms
      render only:   0.2084 ms
    
    
    jinja2 2.9.6
    -------
      import:       68.5041 ms
      complete:      7.1358 ms
      parse only:    6.8045 ms
      render only:   0.3144 ms
