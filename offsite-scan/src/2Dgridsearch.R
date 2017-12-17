rm(list=ls())

library(akima)
library(lattice)

df <- read.csv("./log/offsite.log", header = FALSE)

Q <- df[,1]
R <- df[,2]
Err <- df[,3]

Errmin <- min(Err)

Rmin <- R[which(Err==Errmin)]
Qmin <- Q[which(Err==Errmin)]

Rreg <- R[which(Err<1.1*Errmin)]
Qreg <- Q[which(Err<1.1*Errmin)]

fit <- lm(Qreg ~ I(0 + 1/Rreg))
Rfit <- seq(min(R), max(R), (max(R)-min(R))/1000)
Qfit <- predict(fit, list(Rreg=Rfit))

reggrid <- interp(R, Q, Err,
                 linear=T, extrap=F,
                 nx=1000, ny=1000)
reggridlog <- reggrid
reggridlog$z <- log10(reggrid$z)

levels <- seq(min(Err), max(Err), diff(range(Err)) * 0.01)

# X11()

plot(R, Q, xlab="R", ylab="Q",
    type="n")
contour(reggrid, add=TRUE, lev = levels)
#image(reggridlog, add=TRUE)
# points(Rreg, Qreg)

lines(Rfit, Qfit, col="red")
#constraint <- locator(2)$x

#cat("Lower limit:\t")
#Rmin <- readLines(con="stdin", 1)
#cat("Lower limit:\t")
#Rmax <- readLines(con="stdin", 1)
constraint <- c(0.01, 3.0)#Rmin, Rmax)

abline(v=constraint)

N <- length(Rfit)

Rout <- Rfit[which(Rfit <= max(constraint) & Rfit >= min(constraint))]
Qout <- Qfit[which(Rfit <= max(constraint) & Rfit >= min(constraint))]

write(length(Rout), file="./log/fitdata.log")
write.table(data.frame(Rout, Qout), file = "./log/fitdata.log", append=TRUE, row.names = FALSE, col.name = FALSE, sep="\t")
