'use strict';
// Horizontal low-Mach homogeneous mixture screening relation. No separator/nozzle.
// Delta P = viscousResistance*m + inertialResistance*m*abs(m).
// Viscous loss dominates at zero flow; specified Darcy f and minor K describe
// distributed/local inertial losses. Neither viscosity nor f is calibrated here.
function coefficients(donor,connection){
 const {diameterM:D,lengthM:L,viscosityPaS:mu,darcyF:f,minorK:K}=connection,A=Math.PI*D*D/4,rho=donor.rho;
 return {linear:128*mu*L/(Math.PI*D**4*rho),quadratic:(f*L/D+K)/(2*rho*A*A)};
}
function pressureDropPa(massFlowKgS,donor,connection){const c=coefficients(donor,connection);return c.linear*massFlowKgS+c.quadratic*massFlowKgS*Math.abs(massFlowKgS);}
function connectionFlow(left,right,connection){
 const dp=(left.p-right.p)*1e5;if(dp===0)return 0;
 if(connection.checkValve&&dp<0)return 0;
 const donor=dp>0?left:right,c=coefficients(donor,connection),magnitude=2*Math.abs(dp)/(c.linear+Math.sqrt(c.linear*c.linear+4*c.quadratic*Math.abs(dp)));
 return Math.sign(dp)*magnitude;
}
module.exports={coefficients,pressureDropPa,connectionFlow};
