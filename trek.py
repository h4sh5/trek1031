#!/usr/bin/env python3
import random
import os
import sys
import math

DEBUG=False

if os.getenv("DEBUG") != None:
	DEBUG=True

def dlog(*args, **kwargs):
	if DEBUG:
		print(*args, file=sys.stderr, **kwargs)

class TrekGame:
	'''
	class for a trek game, with a x_y grid for each sector and 
	xy grid for each quadrant

	inspired by: https://docs.freebsd.org/44doc/usd/31.trek/paper.html
	^ not true to implementation
	'''


	def make_sector(self, qx,qy, starbases, klingons):
		sector = []
		ASTEROID_CHANCE = 20 # 1 out of whatever this number is

		starbases_xy = []
		klingons_xy = []

		for i in range(klingons):
			klingons_xy.append((random.randrange(self.sect_x), random.randrange(self.sect_y)))
		for i in range(starbases):
			starbases_xy.append((random.randrange(self.sect_x), random.randrange(self.sect_y)))



		for x in range(self.sect_x):
			sector.append([])
			for y in range(self.sect_y):
				sector[x].append(self.sprites['empty'])
				# xy = (x,y)
				if (x,y) in starbases_xy:
					sector[x][y] = self.sprites['starbase']
				elif (x,y) in klingons_xy:
					sector[x][y] = self.sprites['klingon']
				elif random.randrange(ASTEROID_CHANCE) == 1:
					if sector[x][y] == '.': # only if position is empty
						sector[x][y] = self.sprites['asteroid'] 
		# dlog(sector)
		return sector

	def make_map(self):
		# each quadrant is a sect_x * sect_y grid

		self.map = []

		# calculate star base numbers based on num. quadrants
		QUADRANTS_STARBASE_RATIO = 0.05
		
		starbases = int(QUADRANTS_STARBASE_RATIO * self.quadrants)
		starbase_quads = []
		for x in range(starbases):
			# get quandrant number of each klingon
			s = (random.randrange(self.quad_x), random.randrange(self.quad_y))
			starbase_quads.append(s)
		dlog("starbase_quads:", starbase_quads)

		klingon_quads = []
		for x in range(self.klingons):
			# get quandrant number of each klingon
			s = (random.randrange(self.quad_x), random.randrange(self.quad_y))
			klingon_quads.append(s)
		dlog("klingon_quads:", klingon_quads)

		for x in range(self.quad_x):
			self.map.append([])
			for y in range(self.quad_y):
				# self.map[x].append([])
				self.map[x].append(self.make_sector(y, x, starbase_quads.count((y,x)), klingon_quads.count((y,x))))
		# for i in self.map:
			# for s in i:
				# dlog(s)

	def print_quadrant(self, q):

		print(" "+ " _ "*self.sect_y)
		for x in range(self.sect_x):
			print('|',end='')
			for y in range(self.sect_y):
				# print(q[x],q[y], end='')
				print(' '+q[x][y]+' ',end='')
			print('|')
		print(" "+ " - "*self.sect_y)

	def print_current_quadrant(self):
		self.print_quadrant(self.map[self.current_quad[0]][self.current_quad[1]])

	def dump_map(self):
		for qx in range(self.quad_x):
			for qy in range(self.quad_y):
				print('quadrant %d,%d' %(qx,qy))
				# dlog(self.map[qx])
				q = self.map[qx][qy]
				self.print_quadrant(q)

	def get_location(self, quadxy, sectxy):
		qx, qy = quadxy
		sx, sy = sectxy
		return self.map[qx][qy][sx][sy]

	def set_location(self, quadxy, sectxy, c):
		qx, qy = quadxy
		sx, sy = sectxy
		self.map[qx][qy][sx][sy] = c

	def get_trajectory(self, direction, distance=-1, is_warp=False):
		'''
		get trajectory (as a list of x,y tuples) using direction in degrees and 
		distance (-1 means unlimited til the end of the quadrant size)
		'''
		trajectory = []
		rad = math.radians(direction)
		cx, cy = self.current_sector[0], self.current_sector[1]
		if is_warp:	
			cx, cy = self.current_quad[0], self.current_quad[1]
		# step-wise, ends at max distance or end of sector
		d = 1
		while True:
			x1 = int(cx - math.cos(rad) * d)
			y1 = int(cy + math.sin(rad) * d)
			# y1 = int(cx + math.cos(rad) * d)
			# x1 = int(cx - math.sin(rad) * d)
			
			# trajectory.append((x1,y1))
			if is_warp:
				if x1 >= self.quad_x or x1 < 0 or y1 >= self.quad_x or y1 < 0:
					break
			else:
				if x1 >= self.sect_x or x1 < 0 or y1 >= self.sect_y or y1 < 0:
					break
			if distance != -1 and d > distance:
				break
			if not is_warp:
				dlog(f"traj {x1} {y1}:{self.get_location(self.current_quad, (x1,y1))}")
			else:
				dlog(f"traj {x1} {y1}")
			trajectory.append((x1,y1))
			d += 1
		dlog(trajectory)
		return trajectory

	def destroy_object(self, quadxy, sectxy):
		print(f'destroyed {self.objects[self.get_location(self.current_quad, sectxy)]} at {sectxy}')
		self.set_location(quadxy, sectxy, self.sprites['empty'])

	def fire_torpedo(self,direction):
		if self.shield_up:
			miss = random.randrange(2)
			if miss == 1:
				print("Torpedo missed.")
				return
		traj = self.get_trajectory(direction)

		hit = False
		for step in traj:
			if self.get_location(self.current_quad, step) != self.sprites['empty']:
				# hit something
				hit = True
				break

		if hit:
			if self.get_location(self.current_quad, step) != self.SHIP:
				self.destroy_object(self.current_quad, step)
		else:
			print('didn hit anything.')
		self.torpedos -= 1



	def handle_gameover(self, win=False):
		self.gameover = True
		if not win:
			print("game over, you died!")
		else:
			print("game over, you won!")

	def check_gameover(self):
		if self.gameover:
			self.handle_gameover()
			return True
		elif self.klingons <= 0:
			self.handle_gameover(win=True)
			return True
		elif self.energy <= 0:
			self.handle_gameover()
			return True
		return False

	def day(self):
		'''
		each 'tick' of the game. new things happen.
		this function should be call every time something that 'spends time'
		happens, such as movement, firing, scans, etc.
		- klingons attack

		'''

	def print_long_range_scan_map(self):
		total_klingons = 0
		for x in range(self.quad_x):
			for y in range(self.quad_y):
				q_asteroids = 0
				q_klingons = 0
				q_starbases = 0
				for cx in range(self.sect_x):
					for cy in range(self.sect_y):
						if self.get_location((x,y), (cx,cy)) == '.':
							continue
						elif self.objects[self.get_location((x,y), (cx,cy))] == 'klingon':
							q_klingons+=1
							total_klingons += 1
						elif self.objects[self.get_location((x,y), (cx,cy))] == 'asteroid':
							q_asteroids += 1
						elif self.objects[self.get_location((x,y), (cx,cy))] == 'starbase':
							q_starbases += 1
				if q_klingons > 9:
					q_klingons = '+'
				if q_starbases > 9:
					q_starbases = '+'
				if q_asteroids > 9:
					q_asteroids = '+'
				if (x,y) == self.current_quad:
					print(f"{q_klingons}{q_starbases}{q_asteroids}",end='*')
				else:
					print(f"{q_klingons}{q_starbases}{q_asteroids}",end=' ')
			print()
			# update klingons count
			self.klingons = total_klingons

	def lrs(self):
		'''
		long range scan

		actually scan every quadrant, and return a 3 number triple:
		asteroids,bases,klingons
		'''
		self.energy -= 50
		self.print_long_range_scan_map()



	def impulse(self, direction, distance):
		'''
		move the ship to a different location
		'''
		# new location = last element/step of trajectory 
		traj = self.get_trajectory(direction, distance)
		if len(traj) == 0:
			print("Invalid headings.")
			return
		newx,newy = traj[-1]
		# check collisions

		dlog('new xy:', newx,newy)
		for xy in traj:
			x,y = xy
			if self.get_location(self.current_quad, (x, y)) != '.' and self.get_location(self.current_quad,(x,y)) != self.sprites['starbase']:
				# you hit something without shields, you die
				print("Crashed ship into", self.objects[self.get_location(self.current_quad, (x,y))])
				if not self.shield_up:
					self.energy = 0
					self.gameover = True
					return
				else:
					self.energy -= 200
					return
		# TODO handle starbase docking


		
		# change old coords on the map to empty then fill new ones
		self.set_location(self.current_quad, self.current_sector, '.')
		self.current_sector = (newx, newy)
		self.set_location(self.current_quad, self.current_sector, self.SHIP)
		if self.shield_up:
			self.energy -= len(traj) * 2
		else:
			self.energy -= len(traj)

	def warp(self, direction, distance):
		'''
		move the ship to a different quadrant

		basically the same as impulse, but without collisions

		XXX currently does not do collisions, so if you hit something you get
		a free hit
		'''
		# new location = last element/step of trajectory 
		traj = self.get_trajectory(direction, distance, is_warp=True)
		if len(traj) == 0:
			print("Invalid headings.")
			return
		newx,newy = traj[-1]

		dlog('new xy:', newx,newy)
		
		# change old coords on the map to empty then fill new ones
		self.set_location(self.current_quad, self.current_sector, '.')
		self.current_quad = (newx, newy)
		self.set_location(self.current_quad, self.current_sector, self.SHIP)
		if self.shield_up:
			self.energy -= len(traj) * 50 * 2
		else:
			self.energy -= len(traj) * 50

	def jump(self, quadxy, sectxy):
		'''
		use the spore drive to instantly jump to a specific coordinate
		'''
		# validate coordinates
		try:
			self.get_location(quadxy,sectxy)
		except:
			print("Invalid coordinates entered.")
			return
		if self.shield_up:
			print("Cannot jump when shields are up.")
			return


		self.energy -= 1000

		self.set_location(self.current_quad, self.current_sector, self.sprites['empty'])
		self.current_quad = quadxy
		self.current_sector = sectxy
		# crash?
		if self.get_location(quadxy, sectxy) != self.sprites['empty']:
			print(f"Crashed into {self.objects[self.get_location(quadxy, sectxy)]} at {quadxy}:{sectxy}")
			self.gameover = True
			self.energy = 0

		self.set_location(self.current_quad, self.current_sector, self.SHIP)
		

		




	def __init__(self, sect_x, sect_y, quad_x, quad_y, klingons, torpedos, energy=5000, days=500):
		self.sprites = {'klingon':'K', 'asteroid':'*', 'starbase':'B', 'discovery':'D', 'empty':'.'}
		self.objects = dict([(self.sprites.get(x), x) for x in self.sprites.keys()]) # inverse mapping
		self.SHIP = self.sprites['discovery']

		self.gameover = False

		self.sect_x = sect_x 
		self.sect_y = sect_y
		self.quad_x = quad_x
		self.quad_y = quad_y
		self.quadrants = self.quad_x * self.quad_y

		self.max_torpedos = torpedos
		self.torpedos = torpedos
		self.max_energy = energy
		self.energy = energy
		self.shield_up = False
		self.days = days
		self.klingons = klingons

		self.make_map()

		# self.dump_map()

		# start game in a random quadrant and sector location
		while True:
			self.current_quad = (random.randrange(self.quad_x), random.randrange(self.quad_y))
			self.current_sector = (random.randrange(self.sect_x), random.randrange(self.sect_y))
			if self.get_location(self.current_quad, self.current_sector) == '.':
				self.set_location(self.current_quad, self.current_sector, self.SHIP)
				break

	def shield(self, is_up):

		self.shield_up = is_up

	def print_game(self):
		'''
		print current game information including a sector map, location, current ship status,
		commands etc.
		'''
		self.print_current_quadrant()
		print(f'Quadrant {self.current_quad[0]}-{self.current_quad[1]} Sector {self.current_sector[0]},{self.current_sector[1]}')
		print(f"Klingons left: {self.klingons}")
		print(f"Energy {self.energy}")
		print(f"Torpedos {self.torpedos}")
		print(f"Shield up? {self.shield_up}")

	def print_help(self):
		print('h/? - help')
		print('t/torpedo <direction> - fire a torpedo towards x,y sector coordinate')
		print('p/phasor <energy> - fire phasors, aimed automatically towards targets')
		print('i/impulse <direction> <distance> - move using impulse engine towards a direction (0-360 degrees). costs 1 energy per distance')
		print('w/warp <direction> - warp to move towards a quardant. costs 50 energy per quadrant')
		print('j/jump <qx> <qy> <sx> <sy> - use Discovery\'s spore drive to jump to a quardant and sector location. costs 1000 energy. If you jump into an object you will crash!')
		print('s/shield <y/n> - put shields up or down. When up, discovery cannot jump, impulse and warp engines use twice the energy, and firing accuracy decreases to 50%.')
		print('l/lrs - do a long range scan to get number of klingons,starbases and asteroids in each quadrant. costs 50 energy')



if __name__ == "__main__":

	# sector dimensions
	sx,sy = 10,10
	# quadrant dimensions
	qx,qy = 8,8
	klingons = 20
	torpedos = 10
	game = TrekGame(sx, sy, qx, qy, klingons,torpedos)

	print("""

  _____________________
 |_____________]###[___>
              `--.__`-->
                    |~~~\\       ____
                    |----`-._--'----`--____
                    >___|======================
  __________________/__,--<~~~`-------'~~~
 |_____________]###[___>__/


	""")
	print("Welcome onboard the USS Discovery, NCC-1031. You have been tasked with winning the war against the Klingons for Starfleet. Good luck!")
	while True:
		game.print_game()
		c = input("> ")
		if c.startswith('h') or c.startswith('?'):
			game.print_help()
		if c.startswith('t'):
			direction = 0
			try:
				direction = int(c.split()[1])
			except:
				print('invalid direction, must be an integer from 0-359')
				continue
			game.fire_torpedo(direction)

		if c.startswith('i'):
			direction = 0
			distance = 0
			try:
				direction = int(c.split()[1])
			except:
				print('invalid direction, must be an integer from 0-359')
				continue
			try:
				distance = int(c.split()[2])
				if distance < 0:
					raise Exception("invalid distance, must be a positive integer")
			except:
				print('invalid distance, must be a positive integer')
				continue
			game.impulse(direction, distance)
			# game.get_trajectory(direction, distance)

		if c.startswith('s'):
			try:
				choice = c.split()[1]
			except:
				print("missing argument")
				continue
			if choice == 'y':
				game.shield(True)
			if choice == 'n':
				game.shield(False)
			else:
				print('invalid choice, must be y/n')
		if c.startswith('l'):
			game.lrs()

		if c.startswith('w'):
			direction = 0
			distance = 0
			try:
				direction = int(c.split()[1])
			except:
				print('invalid direction, must be an integer from 0-359')
				continue
			try:
				distance = int(c.split()[2])
				if distance < 0:
					raise Exception("invalid distance, must be a positive integer")
			except:
				print('invalid distance, must be a positive integer')
				continue
			game.warp(direction,distance)

		if c.startswith('j'):
			try:
				qx,qy,sx,sy = [int(x) for x in c.split()[1:]]
			except Exception as e:
				print('invalid coordinates:',e)
			game.jump((qx,qy), (sx,sy))

		if game.check_gameover():
			break
