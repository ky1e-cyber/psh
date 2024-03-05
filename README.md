# psh
shell-like system scripting language on python vm

## Examples

Functions
```
// returns string 
let hello = fn(name) {
  return "Hello " + name
}

// returns unit
let echo_hello = fn(name) {
  echo hello(name)
}

echo_hello("Ivan")
```

