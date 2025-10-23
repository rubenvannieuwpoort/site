# To run the program, we first have to compile it.
$ kotlinc main.kt -include-runtime -d main.jar

$ ls
main.kt Main.jar

# Then, we can run the resulting jar file.
$ java -jar Main.jar
Hello, world!
