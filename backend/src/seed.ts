import { PrismaClient } from '@prisma/client';
import bcryptjs from 'bcryptjs';

const prisma = new PrismaClient();

// Mock Teams Data - NBA 2024-2025
const teamsData = [
  {
    name: 'Boston Celtics',
    abbreviation: 'BOS',
    city: 'Boston',
    conference: 'Eastern',
    division: 'Atlantic',
    primaryColor: '#007A33',
    secondaryColor: '#BA3025',
    wins: 5,
    losses: 2,
  },
  {
    name: 'New York Knicks',
    abbreviation: 'NYK',
    city: 'New York',
    conference: 'Eastern',
    division: 'Atlantic',
    primaryColor: '#F58426',
    secondaryColor: '#0851BA',
    wins: 5,
    losses: 2,
  },
  {
    name: 'Miami Heat',
    abbreviation: 'MIA',
    city: 'Miami',
    conference: 'Eastern',
    division: 'Southeast',
    primaryColor: '#98002E',
    secondaryColor: '#F9A01B',
    wins: 4,
    losses: 3,
  },
  {
    name: 'Denver Nuggets',
    abbreviation: 'DEN',
    city: 'Denver',
    conference: 'Western',
    division: 'Northwest',
    primaryColor: '#0E2240',
    secondaryColor: '#FFB81C',
    wins: 5,
    losses: 2,
  },
  {
    name: 'Los Angeles Lakers',
    abbreviation: 'LAL',
    city: 'Los Angeles',
    conference: 'Western',
    division: 'Pacific',
    primaryColor: '#552583',
    secondaryColor: '#FDB827',
    wins: 4,
    losses: 3,
  },
  {
    name: 'Golden State Warriors',
    abbreviation: 'GSW',
    city: 'Golden State',
    conference: 'Western',
    division: 'Pacific',
    primaryColor: '#1D428A',
    secondaryColor: '#FFC52F',
    wins: 3,
    losses: 4,
  },
  {
    name: 'Chicago Bulls',
    abbreviation: 'CHI',
    city: 'Chicago',
    conference: 'Eastern',
    division: 'Central',
    primaryColor: '#CE1141',
    secondaryColor: '#000000',
    wins: 2,
    losses: 5,
  },
  {
    name: 'Phoenix Suns',
    abbreviation: 'PHX',
    city: 'Phoenix',
    conference: 'Western',
    division: 'Pacific',
    primaryColor: '#1D1160',
    secondaryColor: '#E56020',
    wins: 5,
    losses: 2,
  },
  {
    name: 'Milwaukee Bucks',
    abbreviation: 'MIL',
    city: 'Milwaukee',
    conference: 'Eastern',
    division: 'Central',
    primaryColor: '#00471B',
    secondaryColor: '#EEE1C6',
    wins: 6,
    losses: 1,
  },
  {
    name: 'Dallas Mavericks',
    abbreviation: 'DAL',
    city: 'Dallas',
    conference: 'Western',
    division: 'Southwest',
    primaryColor: '#003DA5',
    secondaryColor: '#B8860B',
    wins: 4,
    losses: 3,
  },
];

// Mock Players Data
const playersData = [
  // Celtics
  { firstName: 'Jayson', lastName: 'Tatum', position: 'SF', number: 0, teamId: 1, ppg: 28.5, rpg: 9.2, apg: 4.1 },
  { firstName: 'Jaylen', lastName: 'Brown', position: 'SF', number: 7, teamId: 1, ppg: 25.3, rpg: 8.7, apg: 3.5 },
  { firstName: 'Derrick', lastName: 'White', position: 'SG', number: 9, teamId: 1, ppg: 12.2, rpg: 3.8, apg: 5.1 },
  
  // Knicks
  { firstName: 'Julius', lastName: 'Randle', position: 'PF', number: 30, teamId: 2, ppg: 21.8, rpg: 8.9, apg: 3.2 },
  { firstName: 'Jalen', lastName: 'Brunson', position: 'PG', number: 11, teamId: 2, ppg: 22.5, rpg: 3.5, apg: 7.2 },
  { firstName: 'Josh', lastName: 'Hart', position: 'SG', number: 3, teamId: 2, ppg: 8.5, rpg: 7.2, apg: 2.3 },
  
  // Heat
  { firstName: 'Jimmy', lastName: 'Butler', position: 'SF', number: 22, teamId: 3, ppg: 20.1, rpg: 5.2, apg: 5.3 },
  { firstName: 'Bam', lastName: 'Adebayo', position: 'C', number: 13, teamId: 3, ppg: 15.8, rpg: 10.5, apg: 2.8 },
  
  // Nuggets
  { firstName: 'Nikola', lastName: 'Jokic', position: 'C', number: 15, teamId: 4, ppg: 30.2, rpg: 11.8, apg: 9.7 },
  { firstName: 'Jamal', lastName: 'Murray', position: 'PG', number: 27, teamId: 4, ppg: 20.1, rpg: 3.5, apg: 6.2 },
  
  // Lakers
  { firstName: 'LeBron', lastName: 'James', position: 'SF', number: 23, teamId: 5, ppg: 26.1, rpg: 8.2, apg: 8.3 },
  { firstName: 'Anthony', lastName: 'Davis', position: 'PF', number: 3, teamId: 5, ppg: 25.9, rpg: 12.5, apg: 2.1 },
  
  // Warriors
  { firstName: 'Stephen', lastName: 'Curry', position: 'PG', number: 30, teamId: 6, ppg: 22.1, rpg: 3.2, apg: 6.7 },
  { firstName: 'Klay', lastName: 'Thompson', position: 'SG', number: 11, teamId: 6, ppg: 18.2, rpg: 3.5, apg: 1.8 },
  
  // Bulls
  { firstName: 'DeMar', lastName: 'DeRozan', position: 'SG', number: 11, teamId: 7, ppg: 24.3, rpg: 4.2, apg: 3.1 },
  { firstName: 'Nikola', lastName: 'Vucevic', position: 'C', number: 9, teamId: 7, ppg: 17.8, rpg: 10.2, apg: 2.5 },
  
  // Suns
  { firstName: 'Kevin', lastName: 'Durant', position: 'SF', number: 35, teamId: 8, ppg: 27.1, rpg: 6.7, apg: 5.0 },
  { firstName: 'Shai', lastName: 'Gilgeous-Alexander', position: 'PG', number: 2, teamId: 8, ppg: 26.3, rpg: 5.2, apg: 9.2 },
  
  // Bucks
  { firstName: 'Giannis', lastName: 'Antetokounmpo', position: 'PF', number: 34, teamId: 9, ppg: 30.8, rpg: 11.5, apg: 6.5 },
  { firstName: 'Damian', lastName: 'Lillard', position: 'PG', number: 0, teamId: 9, ppg: 24.3, rpg: 3.8, apg: 7.1 },
  
  // Mavericks
  { firstName: 'Luka', lastName: 'Doncic', position: 'SG', number: 77, teamId: 10, ppg: 33.9, rpg: 8.2, apg: 8.0 },
  { firstName: 'Kyrie', lastName: 'Irving', position: 'PG', number: 2, teamId: 10, ppg: 25.2, rpg: 3.5, apg: 5.8 },
];

// Mock Games Data
const gamesData = [
  {
    homeTeamId: 1, // Celtics
    awayTeamId: 2, // Knicks
    homeScore: 112,
    awayScore: 107,
    gameDate: new Date('2024-11-01T19:30:00Z'),
    status: 'Final',
    season: 2024,
    homeOffRtg: 118.5,
    homeDefRtg: 112.3,
    awayOffRtg: 115.8,
    awayDefRtg: 119.2,
    pace: 96.5,
  },
  {
    homeTeamId: 4, // Nuggets
    awayTeamId: 6, // Warriors
    homeScore: 120,
    awayScore: 110,
    gameDate: new Date('2024-11-02T20:00:00Z'),
    status: 'Final',
    season: 2024,
    homeOffRtg: 125.3,
    homeDefRtg: 108.2,
    awayOffRtg: 112.5,
    awayDefRtg: 116.8,
    pace: 98.2,
  },
  {
    homeTeamId: 5, // Lakers
    awayTeamId: 8, // Suns
    homeScore: 118,
    awayScore: 115,
    gameDate: new Date('2024-11-03T21:30:00Z'),
    status: 'Final',
    season: 2024,
    homeOffRtg: 119.2,
    homeDefRtg: 114.8,
    awayOffRtg: 121.5,
    awayDefRtg: 115.2,
    pace: 97.1,
  },
  {
    homeTeamId: 9, // Bucks
    awayTeamId: 3, // Heat
    homeScore: 125,
    awayScore: 108,
    gameDate: new Date('2024-11-04T20:00:00Z'),
    status: 'Final',
    season: 2024,
    homeOffRtg: 132.1,
    homeDefRtg: 109.5,
    awayOffRtg: 110.2,
    awayDefRtg: 125.8,
    pace: 95.3,
  },
];

// Mock Injuries
const injuriesData = [
  {
    playerId: 3, // Derrick White
    status: 'Day-to-Day',
    description: 'Ankle soreness',
    startDate: new Date('2024-11-01'),
    estimatedReturn: new Date('2024-11-05'),
  },
  {
    playerId: 14, // Klay Thompson
    status: 'Out',
    description: 'Hamstring injury',
    startDate: new Date('2024-10-25'),
    estimatedReturn: new Date('2024-11-15'),
  },
];

async function seed() {
  try {
    console.log('🌱 Starting database seed...');

    // Clear existing data
    await prisma.prediction.deleteMany();
    await prisma.injury.deleteMany();
    await prisma.game.deleteMany();
    await prisma.watchlistPlayer.deleteMany();
    await prisma.favoriteTeam.deleteMany();
    await prisma.player.deleteMany();
    await prisma.team.deleteMany();
    await prisma.user.deleteMany();

    // Seed teams
    console.log('📍 Seeding teams...');
    for (const team of teamsData) {
      await prisma.team.create({ data: team });
    }

    // Seed players
    console.log('🏀 Seeding players...');
    for (const player of playersData) {
      await prisma.player.create({
        data: {
          ...player,
          pointsPerGame: player.ppg,
          reboundsPerGame: player.rpg,
          assistsPerGame: player.apg,
          fieldGoalPercentage: 45 + Math.random() * 10,
          threePointPercentage: 30 + Math.random() * 15,
        },
      });
    }

    // Seed games
    console.log('🎮 Seeding games...');
    for (const game of gamesData) {
      await prisma.game.create({ data: game });
    }

    // Seed injuries
    console.log('🤕 Seeding injuries...');
    for (const injury of injuriesData) {
      await prisma.injury.create({ data: injury });
    }

    // Seed test users
    console.log('👥 Seeding users...');
    const hashedPassword = await bcryptjs.hash('TestPassword123', 10);

    await prisma.user.create({
      data: {
        email: 'admin@courtvision.ai',
        password: hashedPassword,
        firstName: 'Admin',
        lastName: 'User',
        role: 'ADMIN',
        isVerified: true,
      },
    });

    await prisma.user.create({
      data: {
        email: 'premium@courtvision.ai',
        password: hashedPassword,
        firstName: 'Premium',
        lastName: 'User',
        role: 'PREMIUM',
        isVerified: true,
      },
    });

    await prisma.user.create({
      data: {
        email: 'user@courtvision.ai',
        password: hashedPassword,
        firstName: 'Regular',
        lastName: 'User',
        role: 'USER',
        isVerified: true,
      },
    });

    console.log('✅ Database seeded successfully!');
    console.log('\n📊 Seeded data summary:');
    console.log(`   • Teams: ${teamsData.length}`);
    console.log(`   • Players: ${playersData.length}`);
    console.log(`   • Games: ${gamesData.length}`);
    console.log(`   • Injuries: ${injuriesData.length}`);
    console.log(`   • Users: 3 (Admin, Premium, Regular)`);
    console.log('\n🔑 Test Credentials:');
    console.log('   Admin: admin@courtvision.ai / TestPassword123');
    console.log('   Premium: premium@courtvision.ai / TestPassword123');
    console.log('   User: user@courtvision.ai / TestPassword123');
  } catch (error) {
    console.error('❌ Seeding failed:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

seed();
